# todo-mcp-server

A local MCP server for managing tasks, built with [FastMCP](https://github.com/jlowin/fastmcp). Supports priorities, tags, due dates, full-text search, and persistent storage.

## Prerequisites

- Python 3.x
- [uv](https://github.com/astral-sh/uv)
- [claude desktop](https://claude.com/)

## Setup

```bash
pip install fastmcp mcp
pip install "mcp[cli]"  # only needed for MCP Inspector
```

## Running

### mcp dev

Make sure your Python is setup, then run:

```bash

```bash
mcp dev todo_server.py
```

Set the transport to `stdio` with:

```
command: uv
args: run --with mcp python todo_server.py
```

<img width="117" height="240" alt="image" src="https://github.com/user-attachments/assets/82ea131f-254f-40ea-bdbd-cdff5c7f11cb" />


### Claude Desktop

Add the following to your config file and restart Claude Desktop:

- **Windows Store install:** `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Standard install:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "todo": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python", "C:\\full\\path\\to\\todo_server.py"]
    }
  }
}
```

Then restart Claude Desktop.

<img width="796" height="403" alt="image" src="https://github.com/user-attachments/assets/32397e98-e1b7-45b0-a994-f1dbc6233dd0" />


## Storage

Tasks are saved to `tasks.json` in the same directory as `todo_server.py`. The path is resolved relative to the script itself, so it works regardless of what directory the MCP host launches from.

## Tools

| Tool | Description |
|---|---|
| `add_task` | Add a task with optional priority, tags, due date, notes |
| `list_tasks` | List tasks, with optional filters for tag, priority, done |
| `get_task` | Get full details of a single task by ID |
| `update_task` | Update any field of a task |
| `complete_task` | Mark a task as done |
| `uncomplete_task` | Reopen a completed task |
| `remove_task` | Delete a task by ID |
| `clear_done` | Delete all completed tasks |
| `search_tasks` | Full-text search across text, notes, and tags |
| `stats` | Summary counts: total, done, pending, overdue, by priority |
| `list_tags` | List all unique tags in use |
| `due_today` | List tasks due today or overdue |

### Priorities

`1` = high, `2` = medium (default), `3` = low

### Tags

Pass as a comma-separated string: `"work,urgent"`

## Resources

| URI | Description |
|---|---|
| `todo://tasks` | All tasks |
| `todo://tasks/pending` | Pending tasks, sorted by priority |
| `todo://tasks/done` | Completed tasks |
| `todo://stats` | Live stats snapshot |
| `todo://tags` | All tags with their pending tasks |
| `todo://due` | Tasks due today or overdue |


https://github.com/user-attachments/assets/c7f05351-f66c-4db8-9902-2cd45f12d120

