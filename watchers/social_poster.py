#!/usr/bin/env python3
"""
social_poster.py - Auto-post to all social media platforms
Handles: LinkedIn, Facebook, Instagram, Twitter/X

This watcher monitors /Approved/Social/ folder and posts approved content
"""
import os
import sys
import json
import logging
import time
import requests
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_watcher import BaseWatcher


class SocialPoster(BaseWatcher):
    """
    Social Media Auto-Poster
    Posts approved content to LinkedIn, Facebook, Instagram, Twitter
    """

    def __init__(self, vault_path: str = None, check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        self.approved_folder = self.vault_path / 'Approved' / 'Social'
        self.posted_folder = self.vault_path / 'Posted'
        self.failed_folder = self.vault_path / 'Failed_Posts'

        # Create folders
        for folder in [self.approved_folder, self.posted_folder, self.failed_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        self.logger.info("Social Poster initialized")
        self.logger.info(f"Monitoring: {self.approved_folder}")

    def check_for_posts(self):
        """Check for approved posts"""
        if not self.approved_folder.exists():
            return

        post_files = list(self.approved_folder.glob('*.md'))

        if post_files:
            self.logger.info(f"Found {len(post_files)} approved post(s)")

            for post_file in post_files:
                self.process_post(post_file)

    def process_post(self, post_file: Path):
        """Process an approved social media post"""
        try:
            content = post_file.read_text()
            metadata = self._parse_frontmatter(content)

            platform = metadata.get('platform', '').lower()
            self.logger.info(f"Processing {platform} post: {post_file.name}")

            success = False

            if platform == 'linkedin':
                success = self.post_to_linkedin(metadata, content)
            elif platform == 'facebook':
                success = self.post_to_facebook(metadata, content)
            elif platform == 'instagram':
                success = self.post_to_instagram(metadata, content)
            elif platform == 'twitter' or platform == 'x':
                success = self.post_to_twitter(metadata, content)
            elif platform == 'all':
                # Post to all platforms
                results = []
                results.append(self.post_to_linkedin(metadata, content))
                results.append(self.post_to_facebook(metadata, content))
                results.append(self.post_to_instagram(metadata, content))
                results.append(self.post_to_twitter(metadata, content))
                success = all(results)
            else:
                self.logger.warning(f"Unknown platform: {platform}")

            # Move file based on result
            if success:
                dest = self.posted_folder / post_file.name
                self.logger.info(f"✅ Post successful, moving to Posted/")
            else:
                dest = self.failed_folder / post_file.name
                self.logger.error(f"❌ Post failed, moving to Failed_Posts/")

            post_file.rename(dest)

        except Exception as e:
            self.logger.error(f"Error processing post: {e}")

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown"""
        metadata = {}

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                # Parse metadata
                for line in parts[1].strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def post_to_linkedin(self, metadata: dict, content: str) -> bool:
        """Post to LinkedIn using API or Playwright"""
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        profile_urn = os.getenv('LINKEDIN_PROFILE_URN')

        # Extract post content (after frontmatter)
        post_content = self._extract_content(content)

        if access_token and profile_urn:
            return self._post_linkedin_api(access_token, profile_urn, post_content)
        else:
            return self._post_linkedin_playwright(post_content)

    def _post_linkedin_api(self, access_token: str, profile_urn: str, content: str) -> bool:
        """Post to LinkedIn using API"""
        try:
            url = "https://api.linkedin.com/v2/ugcPosts"

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Trim content to 3000 chars (LinkedIn limit)
            if len(content) > 3000:
                content = content[:2997] + '...'

            payload = {
                "author": profile_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code in [200, 201]:
                self.logger.info(f"LinkedIn post successful: {response.json().get('id')}")
                return True
            else:
                self.logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"LinkedIn API error: {e}")
            return False

    def _post_linkedin_playwright(self, content: str) -> bool:
        """Post to LinkedIn using Playwright (auto-login)"""
        try:
            # This would require async/await - simplified for now
            self.logger.warning("LinkedIn Playwright posting requires async implementation")
            return False
        except Exception as e:
            self.logger.error(f"LinkedIn Playwright error: {e}")
            return False

    def post_to_facebook(self, metadata: dict, content: str) -> bool:
        """Post to Facebook page"""
        page_id = os.getenv('FACEBOOK_PAGE_ID')
        access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')

        if not page_id or not access_token:
            self.logger.error("Facebook credentials not configured")
            return False

        try:
            post_content = self._extract_content(content)

            url = f"https://graph.facebook.com/{page_id}/feed"
            data = {
                'message': post_content,
                'access_token': access_token
            }

            response = requests.post(url, data=data, timeout=30)

            if response.status_code in [200, 201]:
                result = response.json()
                self.logger.info(f"Facebook post successful: ID={result.get('id')}")
                return True
            else:
                self.logger.error(f"Facebook error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Facebook error: {e}")
            return False

    def post_to_instagram(self, metadata: dict, content: str) -> bool:
        """Post to Instagram (requires media)"""
        business_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')

        if not business_id or not access_token:
            self.logger.error("Instagram credentials not configured")
            return False

        try:
            # Instagram requires image URL - simplified implementation
            image_url = metadata.get('image_url', '')

            if not image_url:
                self.logger.warning("Instagram post requires image_url in metadata")
                return False

            url = f"https://graph.facebook.com/{business_id}/media"
            data = {
                'image_url': image_url,
                'caption': self._extract_content(content),
                'access_token': access_token
            }

            # Create media container
            response = requests.post(url, data=data, timeout=30)

            if response.status_code in [200, 201]:
                container_id = response.json().get('id')

                # Publish the container
                publish_url = f"https://graph.facebook.com/{business_id}/media_publish"
                publish_data = {
                    'creation_id': container_id,
                    'access_token': access_token
                }

                publish_response = requests.post(publish_url, data=publish_data, timeout=30)

                if publish_response.status_code in [200, 201]:
                    self.logger.info(f"Instagram post successful")
                    return True
                else:
                    self.logger.error(f"Instagram publish error: {publish_response.text}")
                    return False
            else:
                self.logger.error(f"Instagram container error: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Instagram error: {e}")
            return False

    def post_to_twitter(self, metadata: dict, content: str) -> bool:
        """Post to Twitter/X"""
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if not all([api_key, api_secret, access_token, access_secret]):
            self.logger.error("Twitter credentials not configured")
            return False

        try:
            post_content = self._extract_content(content)

            # Trim to 280 chars
            if len(post_content) > 280:
                post_content = post_content[:277] + '...'

            # Using OAuth 1.0a for posting
            import tweepy

            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )

            response = client.create_tweet(text=post_content)

            if response.data:
                self.logger.info(f"Twitter post successful: ID={response.data['id']}")
                return True
            else:
                self.logger.error("Twitter post failed")
                return False

        except ImportError:
            # Fallback to requests if tweepy not available
            return self._post_twitter_raw(post_content)
        except Exception as e:
            self.logger.error(f"Twitter error: {e}")
            return False

    def _post_twitter_raw(self, content: str) -> bool:
        """Post to Twitter using raw requests (OAuth 1.0)"""
        # Simplified - would need OAuth1 signing
        self.logger.warning("Raw Twitter posting not implemented - install tweepy")
        return False

    def _extract_content(self, full_content: str) -> str:
        """Extract actual content from markdown (remove frontmatter)"""
        if '---' in full_content:
            parts = full_content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return full_content.strip()

    def run(self):
        """Main loop"""
        self.logger.info("Social Poster starting...")

        while self.running:
            try:
                self.check_for_posts()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("Social Poster stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)

        self.logger.info("Social Poster stopped")


def main():
    """Main entry point"""
    vault_path = os.getenv('VAULT_PATH',
        Path(__file__).parent.parent / 'AI_Employee_Vault')

    poster = SocialPoster(str(vault_path))
    poster.run()


if __name__ == '__main__':
    main()
