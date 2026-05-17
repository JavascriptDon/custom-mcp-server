# todo-mcp-server

A local MCP server for managing tasks, built with [FastMCP](https://github.com/jlowin/fastmcp). Supports priorities, tags, due dates, full-text search, and persistent storage.

## Prerequisites

- Python 3.x
- [uv](https://github.com/astral-sh/uv)

## Setup

```bash
pip install "mcp[cli]"  # only needed for MCP Inspector
```

## Running

### MCP Inspector

Set the transport to `stdio` with:

```
command: uv
args: run,--with,mcp,python,todo_server.py
```

> The `args` field is a comma-separated string, not a JSON array — that's how the Inspector UI expects it.

> Don't use `mcp run todo_server.py` — it doesn't handle custom classes well and will corrupt the JSON stream.

### Claude Desktop

Add to `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` (Windows Store install — path may vary):

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
