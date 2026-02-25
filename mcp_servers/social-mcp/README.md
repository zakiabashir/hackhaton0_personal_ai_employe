# Social Media MCP Server

Model Context Protocol server for social media posting to Facebook, Instagram, and Twitter (X).

## Setup

1. Install dependencies:
```bash
cd social-mcp
npm install
```

2. Install Playwright browsers:
```bash
npx playwright install chromium
```

3. Configure (optional):

**Twitter API Credentials:**
```bash
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"
```

4. Add to Claude Code MCP config:

```json
{
  "mcpServers": {
    "social": {
      "command": "node",
      "args": ["E:/hackhaton0_personal_ai_employe/mcp_servers/social-mcp/index.js"],
      "env": {
        "VAULT_PATH": "E:/hackhaton0_personal_ai_employe/AI_Employee_Vault"
      }
    }
  }
}
```

## Tools

### create_facebook_post
Create a Facebook post draft for approval.

### create_instagram_post
Create an Instagram post draft (requires image URL).

### create_tweet
Create a Twitter/X post draft (max 280 characters).

### post_to_facebook
Post approved content to Facebook (browser automation).

### post_to_twitter
Post approved content to Twitter (requires API setup).

### generate_content_calendar
Generate a week of social media content across platforms.

### analyze_performance
Generate summary of social media performance.

## Platform-Specific Notes

### Facebook
- Uses browser automation (Playwright)
- Requires manual login first run
- Session saved for subsequent runs

### Instagram
- Drafts created for mobile app posting
- Image URL required
- Hashtags auto-generated

### Twitter/X
- Can use API with credentials
- Or manual posting from draft
- 280 character limit enforced

## Usage Examples

```javascript
// Create Facebook post
create_facebook_post({
  content: "Excited to share our latest AI automation updates!",
  imageUrl: "https://example.com/image.jpg"
})

// Create Instagram post
create_instagram_post({
  content: "Another day of innovation! #AI #Automation",
  imageUrl: "https://example.com/photo.jpg",
  hashtags: "#AI #Automation #Innovation"
})

// Create Tweet
create_tweet({
  content: "Just shipped a new feature! 🚀 #Tech"
})

// Generate weekly calendar
generate_content_calendar({
  platforms: "facebook,instagram,twitter",
  theme: "AI Automation"
})
```

## Approval Workflow

1. Use create_* tool to generate draft
2. Review draft in /Drafts folder
3. Edit if needed
4. Move to /Approved to publish
5. Use post_* tool to execute

## Troubleshooting

**Facebook login issues:**
- Run with headless: false first time
- Complete login in browser window
- Session will be saved

**Twitter posting:**
- Configure API credentials for automation
- Or use manual posting from drafts

**Instagram posting:**
- Currently mobile-app based
- Use drafts as reference for manual posting
