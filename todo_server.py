from typing import List, Optional
from dataclasses import dataclass, field
from mcp.server.fastmcp import FastMCP
import uuid, json, os
from datetime import datetime

mcp = FastMCP("todo")
STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    done: bool = False
    priority: int = 2          # 1=high, 2=medium, 3=low
    tags: List[str] = field(default_factory=list)
    due_date: Optional[str] = None   # ISO date string, e.g. "2025-12-31"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    notes: str = ""

# ── Persistence ────────────────────────────────────────────────────────────────

def load_tasks() -> List[Task]:
    if not os.path.exists(STORAGE_PATH):
        return []
    with open(STORAGE_PATH) as f:
        return [Task(**t) for t in json.load(f)]

def save_tasks():
    with open(STORAGE_PATH, "w") as f:
        json.dump([vars(t) for t in TASKS], f, indent=2, default=str)

TASKS: List[Task] = load_tasks()

def find_task(task_id: str) -> Optional[Task]:
    return next((t for t in TASKS if t.id == task_id), None)

# ── Tools: CRUD ────────────────────────────────────────────────────────────────

@mcp.tool()
async def add_task(
    task: str,
    priority: int = 2,
    tags: str = "",          # comma-separated, e.g. "work,urgent"
    due_date: str = "",      # e.g. "2025-12-31"
    notes: str = "",
) -> str:
    """Add a task. Priority: 1=high, 2=medium, 3=low."""
    t = Task(
        text=task,
        priority=max(1, min(3, priority)),  # clamp to 1-3
        tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
        due_date=due_date or None,
        notes=notes,
    )
    TASKS.append(t)
    save_tasks()
    return f"Added [{t.id}]: {t.text}"

@mcp.tool()
async def list_tasks(
    show_done: bool = False,
    tag: str = "",
    priority: int = 0,       # 0 = no filter
) -> str:
    """List tasks with optional filters."""
    tasks = TASKS if show_done else [t for t in TASKS if not t.done]
    if tag:
        tasks = [t for t in tasks if tag in t.tags]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if not tasks:
        return "No tasks found."
    tasks = sorted(tasks, key=lambda t: (t.done, t.priority))
    lines = []
    for t in tasks:
        status = "✓" if t.done else "○"
        due = f" due:{t.due_date}" if t.due_date else ""
        tags = f" [{', '.join(t.tags)}]" if t.tags else ""
        lines.append(f"[{t.id}] {status} p{t.priority}{due}{tags} {t.text}")
    return "\n".join(lines)

@mcp.tool()
async def get_task(task_id: str) -> str:
    """Get full details of a single task."""
    t = find_task(task_id)
    if not t:
        return f"No task with id {task_id}"
    return (
        f"ID:       {t.id}\n"
        f"Text:     {t.text}\n"
        f"Done:     {t.done}\n"
        f"Priority: {t.priority}\n"
        f"Tags:     {', '.join(t.tags) or 'none'}\n"
        f"Due:      {t.due_date or 'none'}\n"
        f"Notes:    {t.notes or 'none'}\n"
        f"Created:  {t.created_at}\n"
        f"Completed:{t.completed_at or 'not yet'}"
    )

@mcp.tool()
async def update_task(
    task_id: str,
    text: str = "",
    priority: int = 0,
    due_date: str = "",
    notes: str = "",
    tags: str = "",
) -> str:
    """Update any field of a task. Only provided fields are changed."""
    t = find_task(task_id)
    if not t:
        return f"No task with id {task_id}"
    if text:       t.text = text
    if priority:   t.priority = max(1, min(3, priority))
    if due_date:   t.due_date = due_date
    if notes:      t.notes = notes
    if tags:       t.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    save_tasks()
    return f"Updated [{t.id}]"

@mcp.tool()
async def complete_task(task_id: str) -> str:
    """Mark a task as done."""
    t = find_task(task_id)
    if not t:
        return f"No task with id {task_id}"
    t.done = True
    t.completed_at = datetime.now().isoformat()
    save_tasks()
    return f"Completed: {t.text}"

@mcp.tool()
async def uncomplete_task(task_id: str) -> str:
    """Reopen a completed task."""
    t = find_task(task_id)
    if not t:
        return f"No task with id {task_id}"
    t.done = False
    t.completed_at = None
    save_tasks()
    return f"Reopened: {t.text}"

@mcp.tool()
async def remove_task(task_id: str) -> str:
    """Delete a task by ID."""
    global TASKS
    before = len(TASKS)
    TASKS = [t for t in TASKS if t.id != task_id]
    if len(TASKS) == before:
        return f"No task with id {task_id}"
    save_tasks()
    return "Removed."

@mcp.tool()
async def clear_done() -> str:
    """Delete all completed tasks."""
    global TASKS
    removed = sum(1 for t in TASKS if t.done)
    TASKS = [t for t in TASKS if not t.done]
    save_tasks()
    return f"Cleared {removed} completed task(s)."

# ── Tools: Search & Stats ──────────────────────────────────────────────────────

@mcp.tool()
async def search_tasks(query: str) -> str:
    """Full-text search across task text, notes, and tags."""
    q = query.lower()
    matches = [
        t for t in TASKS
        if q in t.text.lower()
        or q in t.notes.lower()
        or any(q in tag for tag in t.tags)
    ]
    if not matches:
        return "No matches."
    return "\n".join(f"[{t.id}] {'✓' if t.done else '○'} {t.text}" for t in matches)

@mcp.tool()
async def stats() -> str:
    """Summary stats: total, done, pending, by priority."""
    total = len(TASKS)
    done = sum(1 for t in TASKS if t.done)
    pending = total - done
    overdue = sum(
        1 for t in TASKS
        if not t.done and t.due_date and t.due_date < datetime.now().date().isoformat()
    )
    by_priority = {1: 0, 2: 0, 3: 0}
    for t in TASKS:
        if not t.done:
            by_priority[t.priority] += 1
    return (
        f"Total: {total} | Done: {done} | Pending: {pending} | Overdue: {overdue}\n"
        f"High priority: {by_priority[1]} | Medium: {by_priority[2]} | Low: {by_priority[3]}"
    )

@mcp.tool()
async def list_tags() -> str:
    """List all unique tags in use."""
    tags = sorted({tag for t in TASKS for tag in t.tags})
    return ", ".join(tags) if tags else "No tags in use."

@mcp.tool()
async def due_today() -> str:
    """List tasks due today or overdue."""
    today = datetime.now().date().isoformat()
    matches = [t for t in TASKS if not t.done and t.due_date and t.due_date <= today]
    if not matches:
        return "Nothing due."
    return "\n".join(
        f"[{t.id}] {'OVERDUE' if t.due_date < today else 'TODAY'} {t.text}"
        for t in sorted(matches, key=lambda t: t.due_date)
    )

# ── Resources ──────────────────────────────────────────────────────────────────

@mcp.resource("todo://tasks")
async def resource_all_tasks() -> str:
    """All tasks as plain text."""
    return await list_tasks(show_done=True)

@mcp.resource("todo://tasks/pending")
async def resource_pending() -> str:
    """Pending tasks only, sorted by priority."""
    return await list_tasks(show_done=False)

@mcp.resource("todo://tasks/done")
async def resource_done() -> str:
    """Completed tasks only."""
    done = [t for t in TASKS if t.done]
    if not done:
        return "No completed tasks."
    return "\n".join(f"[{t.id}] ✓ {t.text} (completed: {t.completed_at})" for t in done)

@mcp.resource("todo://stats")
async def resource_stats() -> str:
    """Live stats snapshot."""
    return await stats()

@mcp.resource("todo://tags")
async def resource_tags() -> str:
    """All tags and the tasks under each one."""
    all_tags = sorted({tag for t in TASKS for tag in t.tags})
    if not all_tags:
        return "No tags."
    sections = []
    for tag in all_tags:
        tagged = [t for t in TASKS if tag in t.tags and not t.done]
        if tagged:
            tasks_str = "\n  ".join(f"[{t.id}] {t.text}" for t in tagged)
            sections.append(f"{tag}:\n  {tasks_str}")
    return "\n\n".join(sections) or "All tagged tasks are done."

@mcp.resource("todo://due")
async def resource_due() -> str:
    """Tasks due today or overdue."""
    return await due_today()

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()