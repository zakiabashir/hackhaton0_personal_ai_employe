"""
LinkedIn Poster - Manages LinkedIn content creation and posting
Uses Playwright for browser automation
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Install with: pip install playwright && playwright install chromium")


class LinkedInPoster(BaseWatcher):
    """Manages LinkedIn posting for business promotion"""

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.linkedin_session'
        self.drafts = self.vault_path / 'Drafts'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.drafts.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)

        # Business hashtags
        self.business_hashtags = [
            '#Automation', '#AI', '#DigitalTransformation', '#BusinessGrowth',
            '#Innovation', '#TechTrends', '#FutureOfWork', '#Entrepreneurship'
        ]

    def generate_post_content(self, topic: str = None, post_type: str = 'business') -> dict:
        """Generate LinkedIn post content based on topic"""

        if post_type == 'business':
            templates = [
                {
                    'topic': 'AI Automation',
                    'content': '''🚀 **The Future of Work is Here**

I'm excited to share how AI automation is transforming businesses in 2026.

Gone are the days of repetitive manual tasks. With AI Employees handling everything from email triage to social media management, business owners can finally focus on what matters most - growth and innovation.

Key benefits we're seeing:
• 85-90% cost reduction per task
• 24/7 availability
• Consistent quality output
• Instant scalability

What's your experience with AI automation? Share in the comments!

👇

'''
                },
                {
                    'topic': 'Digital FTE',
                    'content': '''**Meet Your New Digital Employee** 🤖

Imagine hiring an employee who:
- Works 8,760 hours/year (vs human's 2,000)
- Costs $500-2,000/month (vs $4,000-8,000)
- Requires zero ramp-up time
- Duplicates instantly for scaling

This isn't science fiction. It's what we're building with Digital FTEs.

The question isn't "if" anymore - it's "when will you hire your first AI Employee?

#DigitalFTE #AIAutomation #FutureOfWork
'''
                },
                {
                    'topic': 'Productivity Tips',
                    'content': '''**3 Ways to 10x Your Productivity Today**

1️⃣ **Audit Your Tasks**: Identify repetitive tasks that can be automated
2️⃣ **Build Your Stack**: Use AI tools that integrate with your workflow
3️⃣ **Start Small**: Begin with one automation and expand from there

The goal isn't to replace human creativity - it's to eliminate friction so creativity can flourish.

What's one task you'd love to automate?

#Productivity #Automation #WorkSmarter
'''
                }
            ]
        else:
            templates = []

        if topic:
            for template in templates:
                if topic.lower() in template['topic'].lower():
                    return template

        # Return random template if no specific topic
        return templates[0] if templates else {'topic': 'General', 'content': 'Excited to share updates!'}

    def create_post_draft(self, content: str = None, topic: str = None, post_type: str = 'business') -> Path:
        """Create a LinkedIn post draft for approval"""

        if not content:
            post_data = self.generate_post_content(topic, post_type)
            content = post_data['content']
            topic = post_data['topic']

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_filename = f'LINKEDIN_DRAFT_{timestamp}.md'
        draft_path = self.drafts / draft_filename

        content = f'''---
type: linkedin_post_draft
platform: linkedin
topic: {topic or 'General'}
created: {datetime.now().isoformat()}
status: pending_approval
---

# LinkedIn Post Draft

## Topic: {topic or 'General Business'}

## Post Content:

{content}

---

## Approval Instructions

**To Approve and Post:**
1. Review the post content above
2. Edit if needed
3. Move this file to `/Approved/` folder
4. The post will be published to LinkedIn

**To Reject:**
- Move this file to `/Rejected/` folder

**To Edit:**
- Modify the content above
- Save changes
- Move to `/Approved/` when ready

## Tips for Better Engagement
- Use relevant hashtags
- Tag relevant people
- Include a call-to-action
- Post during peak hours (9-11am, 2-4pm)

---
*Created by LinkedInPoster*
'''

        draft_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Created LinkedIn draft: {draft_filename}")
        return draft_path

    def check_for_updates(self) -> list:
        """Check for approved posts to publish"""
        approved_posts = list(self.pending_approval.glob('LINKEDIN_*.md'))
        return approved_posts

    def create_action_file(self, item: Path) -> Path:
        """Process approved post and create action file"""
        content = item.read_text(encoding='utf-8')

        # Extract post content
        import re
        body_match = re.search(r'## Post Content:\s*\n\n(.+?)(?:\n---\n|\Z)', content, re.DOTALL)
        post_content = body_match.group(1).strip() if body_match else ''

        action_filename = f'POST_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        action_path = self.needs_action / action_filename

        action_content = f'''---
type: linkedin_post
platform: linkedin
status: ready_to_post
created: {datetime.now().isoformat()}
---

# LinkedIn Post Ready to Publish

## Content:

{post_content}

## Instructions
This post has been approved and is ready to publish.

Use LinkedIn automation tool or post manually.
'''

        action_path.write_text(action_content, encoding='utf-8')
        return action_path

    def post_to_linkedin(self, content: str, session_file: str = None) -> bool:
        """Post content to LinkedIn using Playwright (requires authentication)"""

        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available for LinkedIn posting")
            return False

        try:
            with sync_playwright() as p:
                # Launch browser with session if available
                if session_file and Path(session_file).exists():
                    browser = p.chromium.launch_persistent_context(
                        session_file,
                        headless=False
                    )
                else:
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context()
                    context.add_init_script("""
                        // LinkedIn specific overrides
                    """)

                page = browser.new_page()

                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com/feed/')
                page.wait_for_load_state('networkidle')

                # Look for post box
                try:
                    # Click "Start a post" button
                    page.click('button:has-text("Start a post")', timeout=5000)
                    page.wait_for_timeout(1000)

                    # Type content
                    post_box = page.locator('[contenteditable="true"]').first
                    post_box.fill(content)
                    page.wait_for_timeout(1000)

                    # Click post button
                    page.click('button:has-text("Post")', timeout=5000)

                    self.logger.info("Post submitted to LinkedIn")
                    browser.close()
                    return True

                except Exception as e:
                    self.logger.error(f"Error posting to LinkedIn: {e}")
                    browser.close()
                    return False

        except Exception as e:
            self.logger.error(f"LinkedIn automation error: {e}")
            return False

    def generate_weekly_content_calendar(self) -> Path:
        """Generate a week's worth of content ideas"""

        topics = [
            ('Monday', 'Motivation & Goals'),
            ('Tuesday', 'Industry Insights'),
            ('Wednesday', 'Tips & Tricks'),
            ('Thursday', 'Case Studies'),
            ('Friday', 'Team Culture'),
        ]

        calendar_path = self.vault_path / 'Plans' / f'Content_Calendar_{datetime.now().strftime("%Y%m%d")}.md'

        content = f'''# Weekly Content Calendar
**Week of:** {datetime.now().strftime('%Y-%m-%d')}

## Content Plan

'''

        for day, topic in topics:
            post_idea = self.generate_post_content(topic, 'business')
            content += f'''
### {day}: {topic}

**Draft:**

{post_idea['content']}

---

'''

        content += '''
## Usage Instructions

1. Review each day's content
2. Customize as needed
3. Create individual draft files
4. Get approval before posting
5. Track engagement in Logs

---

*Generated by LinkedInPoster*
'''

        calendar_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Created content calendar: {calendar_path}")
        return calendar_path


def main():
    """Main function for LinkedIn poster"""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('--vault', default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--action', choices=['generate', 'post', 'calendar'],
                        default='generate', help='Action to perform')
    parser.add_argument('--topic', help='Topic for post')
    parser.add_argument('--content', help='Custom content for post')

    args = parser.parse_args()

    poster = LinkedInPoster(vault_path=args.vault)

    if args.action == 'generate':
        draft = poster.create_post_draft(content=args.content, topic=args.topic)
        print(f"Created draft: {draft}")

    elif args.action == 'calendar':
        calendar = poster.generate_weekly_content_calendar()
        print(f"Created calendar: {calendar}")


if __name__ == '__main__':
    main()
