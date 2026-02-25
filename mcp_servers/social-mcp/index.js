#!/usr/bin/env node

/**
 * Social Media MCP Server
 * Provides posting capabilities for Facebook, Instagram, and Twitter (X)
 * Implements Model Context Protocol for Claude Code integration
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

// Configuration
const VAULT_PATH = process.env.VAULT_PATH || './AI_Employee_Vault';
const DRAFTS_FOLDER = path.join(VAULT_PATH, 'Drafts');
const APPROVED_FOLDER = path.join(VAULT_PATH, 'Approved');
const SESSIONS_PATH = path.join(VAULT_PATH, '.social_sessions');

// Ensure directories exist
fs.mkdirSync(DRAFTS_FOLDER, { recursive: true });
fs.mkdirSync(APPROVED_FOLDER, { recursive: true });
fs.mkdirSync(SESSIONS_PATH, { recursive: true });

// Create MCP server
const server = new Server(
  {
    name: 'social-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'create_facebook_post',
        description: 'Create a Facebook post draft for approval',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content',
            },
            imageUrl: {
              type: 'string',
              description: 'Optional image URL to attach',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'create_instagram_post',
        description: 'Create an Instagram post draft for approval',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Caption for the post',
            },
            imageUrl: {
              type: 'string',
              description: 'Image URL (required for Instagram)',
            },
            hashtags: {
              type: 'string',
              description: 'Comma-separated hashtags',
            },
          },
          required: ['content', 'imageUrl'],
        },
      },
      {
        name: 'create_tweet',
        description: 'Create a Twitter/X post draft for approval',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Tweet content (max 280 characters)',
            },
            imageUrl: {
              type: 'string',
              description: 'Optional image URL',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'post_to_facebook',
        description: 'Post approved content to Facebook (requires authentication)',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content',
            },
            imageUrl: {
              type: 'string',
              description: 'Optional image URL',
            },
            headless: {
              type: 'boolean',
              description: 'Run headless (default: false for approval)',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'post_to_twitter',
        description: 'Post approved content to Twitter/X (requires API credentials)',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Tweet content',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'generate_content_calendar',
        description: 'Generate a week of social media content',
        inputSchema: {
          type: 'object',
          properties: {
            platforms: {
              type: 'string',
              description: 'Comma-separated platforms (facebook,instagram,twitter)',
            },
            theme: {
              type: 'string',
              description: 'Content theme for the week',
            },
          },
        },
      },
      {
        name: 'analyze_performance',
        description: 'Generate summary of social media performance',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              description: 'Platform to analyze',
              enum: ['facebook', 'instagram', 'twitter', 'all'],
            },
            period: {
              type: 'string',
              description: 'Time period (week, month)',
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'create_facebook_post': {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const draftFilename = `FACEBOOK_DRAFT_${timestamp}.md`;
        const draftPath = path.join(DRAFTS_FOLDER, draftFilename);

        const draftContent = `---
type: facebook_post_draft
platform: facebook
created: ${new Date().toISOString()}
status: pending_approval
---

# Facebook Post Draft

## Content:

${args.content}

${args.imageUrl ? `\n## Image:\n${args.imageUrl}\n` : ''}

---

## Approval Instructions

**To Approve and Post:**
1. Review the post above
2. Edit if needed
3. Move this file to /Approved/ folder
4. Use post_to_facebook tool to publish

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Social Media MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Facebook post draft created: ${draftFilename}\n\nMove to /Approved/ when ready to post.`,
          }],
        };
      }

      case 'create_instagram_post': {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const draftFilename = `INSTAGRAM_DRAFT_${timestamp}.md`;
        const draftPath = path.join(DRAFTS_FOLDER, draftFilename);

        const hashtags = args.hashtags || '#business #innovation #automation';

        const draftContent = `---
type: instagram_post_draft
platform: instagram
created: ${new Date().toISOString()}
status: pending_approval
---

# Instagram Post Draft

## Caption:

${args.content}

## Image:

${args.imageUrl}

## Hashtags:

${hashtags}

---

## Approval Instructions

**To Approve and Post:**
1. Review the post above
2. Edit caption/hashtags if needed
3. Move this file to /Approved/ folder
4. Use Instagram mobile app or automation to publish

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Social Media MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Instagram post draft created: ${draftFilename}\n\nMove to /Approved/ when ready to post.`,
          }],
        };
      }

      case 'create_tweet': {
        const content = args.content.substring(0, 280); // Twitter limit
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const draftFilename = `TWITTER_DRAFT_${timestamp}.md`;
        const draftPath = path.join(DRAFTS_FOLDER, draftFilename);

        const draftContent = `---
type: twitter_post_draft
platform: twitter
created: ${new Date().toISOString()}
status: pending_approval
---

# Twitter/X Post Draft

## Tweet (${content.length}/280 characters):

${content}

${args.imageUrl ? `\n## Image:\n${args.imageUrl}\n` : ''}

---

## Approval Instructions

**To Approve and Post:**
1. Review the tweet above
2. Edit if needed (keep under 280 chars)
3. Move this file to /Approved/ folder
4. Use post_to_twitter tool to publish

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Social Media MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Twitter post draft created: ${draftFilename}\n\nCharacter count: ${content.length}/280\n\nMove to /Approved/ when ready to post.`,
          }],
        };
      }

      case 'post_to_facebook': {
        // Use Playwright for browser automation
        const sessionPath = path.join(SESSIONS_PATH, 'facebook');

        const browser = await chromium.launchPersistentContext(
          sessionPath,
          { headless: args.headless || false }
        );

        const page = await browser.newPage();

        await page.goto('https://www.facebook.com');

        // Wait for user to be logged in
        await page.waitForLoadState('networkidle');

        // Look for post box
        try {
          await page.waitForSelector('[aria-label*="What"', { timeout: 10000 });
          const postBox = await page.locator('[aria-label*="What"]').first();
          await postBox.click();
          await postBox.fill(args.content);

          if (args.imageUrl) {
            // Add image (would need additional implementation)
          }

          // Find and click post button
          const postButton = page.getByText('Post').first();
          await postButton.click();

          await browser.close();

          return {
            content: [{
              type: 'text',
              text: `Facebook post published successfully!`,
            }],
          };
        } catch (error) {
          await browser.close();
          return {
            content: [{
              type: 'text',
              text: `Error posting to Facebook: ${error.message}\n\nPlease ensure you're logged in to Facebook.`,
            }],
            isError: true,
          };
        }
      }

      case 'post_to_twitter': {
        // Check for Twitter API credentials
        const apiKey = process.env.TWITTER_API_KEY;
        const apiSecret = process.env.TWITTER_API_SECRET;
        const accessToken = process.env.TWITTER_ACCESS_TOKEN;
        const accessSecret = process.env.TWITTER_ACCESS_SECRET;

        if (!apiKey || !apiSecret || !accessToken || !accessSecret) {
          return {
            content: [{
              type: 'text',
              text: `Twitter API credentials not configured.\n\nSet the following environment variables:\n- TWITTER_API_KEY\n- TWITTER_API_SECRET\n- TWITTER_ACCESS_TOKEN\n- TWITTER_ACCESS_SECRET\n\nOr post manually via Twitter web interface.`,
            }],
            isError: true,
          };
        }

        // Would use twitter-api-v2 here
        // For now, return instructions
        return {
          content: [{
            type: 'text',
            text: `Twitter posting requires manual execution or full API setup.\n\nContent to post:\n${args.content}\n\nPlease post manually or configure Twitter API credentials.`,
          }],
        };
      }

      case 'generate_content_calendar': {
        const platforms = args.platforms ? args.platforms.split(',') : ['facebook', 'instagram', 'twitter'];
        const theme = args.theme || 'Business Automation';

        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        let calendarContent = `# Social Media Content Calendar\n**Theme:** ${theme}\n**Week of:** ${new Date().toLocaleDateString()}\n\n`;

        days.forEach((day, index) => {
          calendarContent += `\n## ${day}\n\n`;

          platforms.forEach(platform => {
            const postTypes = {
              facebook: 'Business update with image',
              instagram: 'Visual content with story',
              twitter: 'Quick tip or insight'
            };

            calendarContent += `### ${platform.charAt(0).toUpperCase() + platform.slice(1)}\n`;
            calendarContent += `**Type:** ${postTypes[platform]}\n`;
            calendarContent += `**Suggested Topic:** ${theme} - Day ${index + 1} focus\n\n`;
          });
        });

        const calendarPath = path.join(DRAFTS_FOLDER, `Content_Calendar_${Date.now()}.md`);
        fs.writeFileSync(calendarPath, calendarContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Content calendar generated: ${path.basename(calendarPath)}\n\nThemes for ${platforms.join(', ')}\n\nReview and customize before execution.`,
          }],
        };
      }

      case 'analyze_performance': {
        const platform = args.platform || 'all';
        const period = args.period || 'week';

        // Generate a summary report
        const summaryPath = path.join(VAULT_PATH, 'Audit', `Social_Media_Summary_${Date.now()}.md`);
        fs.mkdirSync(path.dirname(summaryPath), { recursive: true });

        const summaryContent = `# Social Media Performance Summary

**Period:** Last ${period}
**Platform:** ${platform.toUpperCase()}
**Generated:** ${new Date().toISOString()}

## Metrics Summary

| Metric | Value |
|--------|-------|
| Posts Published | Track in logs |
| Engagement Rate | Calculate from analytics |
| Follower Growth | Monitor dashboard |
| Top Performing Content | Review logs |

## Recommendations

1. Review top-performing content types
2. Adjust posting schedule based on engagement
3. Focus on high-engagement platforms
4. Create more content like top performers

## Detailed Analysis

See platform-specific analytics dashboards for detailed data.

---
*Generated by Social Media MCP Server*
`;

        fs.writeFileSync(summaryPath, summaryContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Performance summary generated.\n\nLocation: ${summaryPath}\n\nTrack actual metrics by reviewing logs and platform analytics.`,
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Error: ${error.message}`,
      }],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Social Media MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
