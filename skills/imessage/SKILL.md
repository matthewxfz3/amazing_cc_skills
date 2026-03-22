---
name: imessage
description: Read, search, and send iMessages on macOS. Use when the user mentions 'imessage,' 'text message,' 'send a text,' 'read messages,' 'message history,' 'iMessage,' 'SMS,' 'check my messages,' 'text Saloni,' 'message conversation,' or wants to interact with Apple Messages.
dangerous: true
dangerous_reason: Reads local macOS Messages database (~/Library/Messages/chat.db) directly. Requires Full Disk Access. For debugging and personal use only — not intended for scalable or production deployment.
---

# iMessage

Read, search, and send iMessages via the local macOS Messages database.

## DANGER WARNING

This skill accesses your local iMessage database directly by reading `~/Library/Messages/chat.db` (SQLite). This is:
- **For debugging and personal use only**
- **Not scalable** — works only on the local Mac with Full Disk Access
- **Not an official Apple API** — reads internal database format that may change between macOS versions
- **Privacy-sensitive** — gives access to all message history on this machine

For scalable messaging, use proper APIs: Telegram Bot API, WhatsApp Business API, or Slack API.

## Prerequisites

1. **Full Disk Access** for your terminal: System Settings → Privacy & Security → Full Disk Access → enable your terminal app
2. **MCP server installed**: `claude mcp add imessage -- uvx --with "mcp[cli]<1.9" mac-messages-mcp`

## Available Tools

Once the MCP server is connected, these tools are available:

| Tool | What It Does |
|------|-------------|
| `tool_get_chats` | List all conversations (individual + group) |
| `tool_get_recent_messages` | Read recent messages, filter by contact and time range |
| `tool_find_contact` | Fuzzy search contacts by name |
| `tool_check_contacts` | List all contacts in address book |
| `tool_fuzzy_search_messages` | Search message content with fuzzy matching |
| `tool_send_message` | Send iMessage or SMS to a contact, phone, or group chat |
| `tool_check_imessage_availability` | Check if a number supports iMessage vs SMS |
| `tool_check_db_access` | Diagnose database connection issues |
| `tool_check_addressbook` | Diagnose address book access issues |

## Common Workflows

### Read recent messages from a contact
1. `tool_find_contact` with their name (fuzzy match)
2. `tool_get_recent_messages` with the contact name and hours to look back

### Search for specific content
1. `tool_fuzzy_search_messages` with search term and time range
2. Adjust threshold (0.0-1.0) for broader or narrower matching

### Send a message
1. `tool_find_contact` to verify the recipient
2. `tool_send_message` with recipient and message text
3. For group chats, use `tool_get_chats` first to get the chat ID, then `tool_send_message` with `group_chat=true`

## How It Works

```
Messages.app → writes to → ~/Library/Messages/chat.db
                                     ↑
                           MCP server reads via SQLite
                           (no network, no Apple API, all local)

Sending: MCP server → AppleScript → Messages.app → iMessage/SMS
```

## Limitations

- macOS only
- Requires Full Disk Access (broad permission)
- Database schema may change between macOS versions
- No real-time message streaming (poll-based)
- Sending uses AppleScript (may trigger macOS permission dialogs)
