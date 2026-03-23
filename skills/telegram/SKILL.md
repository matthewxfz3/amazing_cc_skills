---
name: telegram
description: Connect Claude Code to Telegram via the official Channels plugin or third-party MCP servers. Use when the user mentions 'telegram,' 'telegram bot,' 'telegram channel,' 'connect to telegram,' 'telegram MCP,' 'telegram notifications,' 'message me on telegram,' 'telegram integration,' or wants to send/receive Telegram messages from Claude Code.
---

# Telegram

Connect Claude Code to Telegram for two-way messaging via the official Channels plugin or third-party MCP servers.

## Option 1: Official Claude Code Channels Plugin (Recommended)

The official Anthropic plugin bridges a Telegram bot to your running Claude Code session. Requires Claude Code v2.1.80+ and claude.ai login.

### Prerequisites

1. **Bun** installed: `curl -fsSL https://bun.sh/install | bash`
2. **Claude Code v2.1.80+** with claude.ai login (API keys not supported)
3. **Telegram bot token** from @BotFather

### Setup

1. Open Telegram, message `@BotFather`, send `/newbot`
2. Choose a display name and username (must end in `bot`, e.g. `my_assistant_bot`)
3. Copy the token BotFather gives you (including the leading number and colon)
4. The token is stored at `~/.claude/channels/telegram/.env`
5. Start Claude Code with the channel:
   ```bash
   claude --channels plugin:telegram@claude-plugins-official
   ```
6. DM your bot on Telegram — it replies with a 6-character pairing code
7. Lock down access:
   ```
   /telegram:access policy allowlist
   ```

### Available Tools

| Tool | What It Does |
|------|-------------|
| `reply` | Send a message to a chat (`chat_id` + `text`). Supports `reply_to` for threading and `files` for attachments |
| `react` | Add an emoji reaction to a message (Telegram's fixed whitelist only) |
| `edit` | Edit a previously sent message |

### How It Works

```
Telegram user → DMs bot → MCP server forwards to Claude Code session
                                        ↓
                              Claude processes + replies
                                        ↓
                              MCP server → Telegram bot → user sees reply
```

- Typing indicator shown automatically while Claude works
- Inbound photos downloaded to `~/.claude/channels/telegram/inbox/`
- Only allowlisted user IDs can interact (pairing captures IDs)

### Limitations

- Claude Code must be running — close terminal = channel goes quiet
- No message history or search — bot only sees messages as they arrive
- Requires claude.ai login (not API keys or Console auth)
- Only Telegram's fixed emoji whitelist for reactions

### Troubleshooting

If Claude Code reports the plugin is not found:
```bash
# Refresh the marketplace
/plugin marketplace update claude-plugins-official

# Or add it manually
/plugin marketplace add anthropics/claude-plugins-official
```

## Option 2: Third-Party MCP Servers

### @s1lverain/claude-telegram-mcp (npm)

Lightweight MCP server with send/receive tools:

```bash
npm install -g @s1lverain/claude-telegram-mcp
claude mcp add telegram -- npx @s1lverain/claude-telegram-mcp
```

Provides `send_telegram_message` and `get_telegram_messages` tools.

### RichardAtCT/claude-code-telegram (GitHub)

Full remote access to Claude Code via Telegram with session persistence:

```bash
git clone https://github.com/RichardAtCT/claude-code-telegram.git
cd claude-code-telegram
npm install
# Configure .env with your bot token
npm start
```

### Composio Telegram Toolkit

Structured MCP integration connecting your AI agent to Telegram:

Visit: https://composio.dev/toolkits/telegram/framework/claude-code

## Common Workflows

### Receive notifications from Claude Code on your phone
1. Set up the official Channels plugin (Option 1)
2. Claude can proactively message you when long-running tasks complete

### Run Claude Code skills from Telegram
1. Configure channels + your skills
2. Message your bot with commands like `/audit-post` or any skill name
3. Claude runs the skill and replies with results in Telegram

### Team notifications
1. Create a Telegram group, add your bot
2. Configure Claude Code to post updates to the group
3. Use `reply` tool with the group's `chat_id`

## Comparison

| Feature | Official Plugin | @s1lverain | RichardAtCT | Composio |
|---------|----------------|------------|-------------|----------|
| Two-way chat | Yes | Yes | Yes | Yes |
| Session persistence | No (needs terminal) | No | Yes | No |
| File attachments | Yes | No | Yes | Yes |
| Reactions | Yes | No | No | No |
| Setup complexity | Low | Low | Medium | Medium |
| Auth required | claude.ai | Bot token | Bot token | Composio account |
