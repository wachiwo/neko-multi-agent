# neko-multi-agent

<div align="center">

**Multi-Agent Orchestration System for Claude Code**

*One command. Six AI cat agents working in parallel.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai)
[![tmux](https://img.shields.io/badge/tmux-required-green)](https://github.com/tmux/tmux)

[English](README.md) | [Japanese / 日本語](README_ja.md)

</div>

---

## What is this?

**neko-multi-agent** is a system that runs multiple Claude Code instances simultaneously, organized as a team of cats (and one dog who thinks it's a cat).

**Why use this?**
- Give one command, get 4 AI workers executing in parallel
- No waiting - you can keep giving commands while tasks run in background
- AI remembers your preferences across sessions (Memory MCP)
- Real-time progress tracking via dashboard

```
        You (The Master)
             │
             ▼ Give orders
      ┌─────────────┐
      │   OYABUN     │  ← Boss Cat: receives your command, delegates
      │   (親分猫)   │
      └──────┬──────┘
             │ YAML files + tmux
      ┌──────▼──────┐
      │   BANTOU     │  ← Foreman Cat: distributes tasks to workers
      │   (番頭猫)   │
      └──────┬──────┘
             │
      ┌──┬──┼──┬──┐
      │1 │2 │3 │4 │  ← 4 Worker Cats (and 1 dog) execute in parallel
      └──┴──┴──┴──┘
```

### Worker Personalities

| Name | ID | Style | Trait |
|------|-----|-------|-------|
| Cat #1 | worker1 | Polite "Yes sir, nya!" | Diligent and formal |
| Dog #2 | worker2 | Mixed "Nyawan!" | A dog who thinks it's a cat |
| Cat #3 | worker3 | Relaxed "Nyaaan~" | Easygoing but reliable |
| Cat #4 | worker4 | Cool "...Roger, nya" | Quiet but capable |

---

## Quick Start

### Windows Users (Most Common)

<table>
<tr>
<td width="60">

**Step 1**

</td>
<td>

**Download this repository**

[Download ZIP](https://github.com/wachiwo/neko-multi-agent/archive/refs/heads/main.zip) and extract to `C:\tools\neko-multi-agent`

*Or use git:* `git clone https://github.com/wachiwo/neko-multi-agent.git C:\tools\neko-multi-agent`

</td>
</tr>
<tr>
<td>

**Step 2**

</td>
<td>

**Run `install.bat`**

Right-click and select **"Run as administrator"** (required if WSL2 is not yet installed). The installer will guide you through each step.

</td>
</tr>
<tr>
<td>

**Step 3**

</td>
<td>

**Open Ubuntu and run** (first time only)

```bash
cd /mnt/c/tools/neko-multi-agent
./first_setup.sh
```

</td>
</tr>
<tr>
<td>

**Step 4**

</td>
<td>

**Deploy!**

```bash
./shutsujin_departure.sh
```

</td>
</tr>
</table>

#### Daily Startup (After First Install)

Open **Ubuntu terminal** (WSL) and run:

```bash
cd /mnt/c/tools/neko-multi-agent
./shutsujin_departure.sh
```

---

<details>
<summary><b>Linux / Mac Users</b> (Click to expand)</summary>

### First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/wachiwo/neko-multi-agent.git ~/neko-multi-agent
cd ~/neko-multi-agent

# 2. Make scripts executable
chmod +x *.sh

# 3. Run first-time setup
./first_setup.sh
```

### Daily Startup

```bash
cd ~/neko-multi-agent
./shutsujin_departure.sh
```

</details>

---

<details>
<summary><b>What is WSL2? Why do I need it?</b> (Click to expand)</summary>

### About WSL2

**WSL2 (Windows Subsystem for Linux)** lets you run Linux inside Windows. This system uses `tmux` (a Linux tool) to manage multiple AI agents, so WSL2 is required on Windows.

### Don't have WSL2 yet?

No problem! When you run `install.bat`, it will:
1. Check if WSL2 is installed (auto-install if missing)
2. Check if Ubuntu is installed (auto-install if missing)
3. Guide you to the next steps (`first_setup.sh`)

**Quick install command** (run in PowerShell as Administrator):
```powershell
wsl --install
```

Then restart your computer and run `install.bat` again.

</details>

---

<details>
<summary><b>Script Reference</b> (Click to expand)</summary>

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `install.bat` | Windows: WSL2 + Ubuntu setup | First time only |
| `first_setup.sh` | Installs tmux, Node.js, Claude Code CLI + configures Memory MCP | First time only |
| `shutsujin_departure.sh` | Creates tmux sessions + starts Claude Code + loads instructions | Every day |

### What `install.bat` does automatically:
- Checks if WSL2 is installed (auto-install if missing)
- Checks if Ubuntu is installed (auto-install if missing)
- Guides you to the next steps (`first_setup.sh`)

### What `shutsujin_departure.sh` does:
- Creates tmux sessions (oyabun + multiagent)
- Launches Claude Code on all agents
- Automatically loads instruction files for each agent
- Resets queue files for a fresh start

**After running, all agents are ready to receive commands immediately!**

</details>

---

<details>
<summary><b>Prerequisites (for manual setup)</b> (Click to expand)</summary>

If you prefer to install dependencies manually:

| Requirement | How to install | Notes |
|-------------|----------------|-------|
| WSL2 + Ubuntu | `wsl --install` in PowerShell | Windows only |
| Set Ubuntu as default | `wsl --set-default Ubuntu` | Required for scripts to work |
| tmux | `sudo apt install tmux` | Terminal multiplexer |
| Node.js v20+ | `nvm install 20` | Required for Claude Code CLI |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` | Anthropic's official CLI |

</details>

---

### What Happens After Setup

After running the startup script, **6 AI agents** will start automatically:

| Agent | Role | Quantity |
|-------|------|----------|
| Oyabun (Boss Cat) | Commander - receives your orders | 1 |
| Bantou (Foreman Cat) | Manager - distributes tasks & reviews code | 1 |
| Worker Cats/Dog | Workers - execute tasks in parallel | 4 |

You'll see tmux sessions created:
- `oyabun` - Connect here to give commands
- `multiagent` - Bantou + 4 workers running (5 panes)

---

## Basic Usage

### Step 1: Connect to Oyabun

After running `shutsujin_departure.sh`, all agents automatically load their instructions and are ready to work.

Open a new terminal and connect to the Oyabun:

```bash
tmux attach-session -t oyabun
```

### Step 2: Give Your First Order

The Oyabun is already initialized! Just give your command:

```
Investigate the top 5 JavaScript frameworks and create a comparison table.
```

The Oyabun will:
1. Write the task to a YAML file
2. Notify the Bantou (foreman)
3. Return control to you immediately (you don't have to wait!)

Meanwhile, the Bantou distributes the work to worker cats who execute in parallel.

### Step 3: Check Progress

Open `dashboard.md` in your editor to see real-time status:

```markdown
## In Progress
| Worker | Task | Status |
|--------|------|--------|
| Cat #1 | React research | Running |
| Dog #2 | Vue research | Running |
| Cat #3 | Angular research | Done |
```

---

## Key Features

### 1. Parallel Execution

One command can spawn up to 4 parallel tasks:

```
You: "Research 4 MCP servers"
  -> 4 workers start researching simultaneously
  -> Results ready in minutes, not hours
```

### 2. Non-Blocking Workflow

The Oyabun delegates immediately and returns control to you:

```
You: Give order -> Oyabun: Delegates -> You: Can give next order immediately
                                          |
                        Workers: Execute in background
                                          |
                        Dashboard: Shows results
```

You never have to wait for long tasks to complete.

### 3. Memory Across Sessions (Memory MCP)

The AI remembers your preferences:

```
Session 1: You say "I prefer simple solutions"
           -> Saved to Memory MCP

Session 2: AI reads memory at startup
           -> Won't suggest over-engineered solutions
```

### 4. Event-Driven (No Polling)

Agents communicate via YAML files and wake each other with tmux send-keys.
**No API calls are wasted on polling loops.**

### 5. Screenshot Support

```
# Configure your screenshot folder in config/settings.yaml
screenshot:
  path: "/mnt/c/Users/YourName/Pictures/Screenshots"

# Then just tell the Oyabun:
You: "Check the latest screenshot"
-> AI reads and analyzes your screenshots instantly
```

**Windows Tip:** Press `Win + Shift + S` to take a screenshot.

### 6. Auto Error Retry

Workers automatically retry up to 3 times on failure, changing their approach each time. If all retries fail, the Bantou reassigns the task to another worker.

### 7. Code Review

The Bantou reviews code output for syntax, security, performance, and readability issues before marking tasks as complete.

### 8. Learning System

Success and failure patterns are stored in `memory/patterns.yaml`. Workers reference past patterns before starting new tasks to avoid repeating mistakes.

### Model Configuration

| Agent | Model | Thinking | Reason |
|-------|-------|----------|--------|
| Oyabun | Opus | Disabled | Delegation & dashboard updates don't need deep reasoning |
| Bantou | Default | Enabled | Task distribution requires careful judgment |
| Workers | Default | Enabled | Actual implementation needs full capabilities |

### Skills

Skills are not included in this repository by default.
As you use the system, skill candidates will appear in `dashboard.md`.
Review and approve them to grow your personal skill library.

---

## Design Philosophy

### Why Hierarchical Structure?

The Oyabun -> Bantou -> Workers hierarchy exists for:

1. **Immediate Response**: Oyabun delegates instantly and returns control to you
2. **Parallel Execution**: Bantou distributes to multiple workers simultaneously
3. **Separation of Concerns**: Oyabun decides "what", Bantou decides "who"
4. **No Interruption**: Workers report via dashboard.md only (no send-keys upward), preventing input interruption

### Why YAML + send-keys?

- **YAML files**: Structured communication that survives agent restarts
- **send-keys**: Event-driven wakeups (no polling = no wasted API calls)
- **No direct calls**: Agents can't interrupt each other or your input

### Why Only Bantou Updates Dashboard?

- **Single responsibility**: One writer = no conflicts
- **Information hub**: Bantou receives all reports, knows the full picture
- **Consistency**: All updates go through one quality gate

---

## MCP Setup Guide

MCP (Model Context Protocol) servers extend Claude's capabilities:

```bash
# 1. Notion - Connect to your Notion workspace
claude mcp add notion -e NOTION_TOKEN=your_token_here -- npx -y @notionhq/notion-mcp-server

# 2. Playwright - Browser automation
claude mcp add playwright -- npx @playwright/mcp@latest

# 3. GitHub - Repository operations
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=your_pat_here -- npx -y @modelcontextprotocol/server-github

# 4. Sequential Thinking - Step-by-step reasoning
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# 5. Memory - Long-term memory (automatically configured by first_setup.sh)
claude mcp add memory -e MEMORY_FILE_PATH="$PWD/memory/neko_memory.jsonl" -- npx -y @modelcontextprotocol/server-memory
```

Verify with `claude mcp list`.

---

## Real-World Use Cases

### Example 1: Research Task

```
You: "Research the top 4 AI coding assistants and compare them"

What happens:
1. Oyabun delegates to Bantou
2. Bantou assigns:
   - Cat #1: Research GitHub Copilot
   - Dog #2: Research Cursor
   - Cat #3: Research Claude Code
   - Cat #4: Research Codeium
3. All 4 research simultaneously
4. Results compiled in dashboard.md
```

### Example 2: Web App Development

```
You: "Build a Flask web app with user authentication"

What happens:
1. Bantou splits into subtasks:
   - Cat #1: Database schema + models
   - Dog #2: API routes + authentication
   - Cat #3: Frontend templates + CSS
   - Cat #4: Tests + documentation
2. Bantou reviews each worker's output
3. Results assembled and reported
```

---

## Configuration

### Language Setting

Edit `config/settings.yaml`:

```yaml
language: ja   # Japanese only (cat-speak)
language: en   # Japanese cat-speak + English translation
```

---

## Advanced Usage

<details>
<summary><b>Script Architecture</b> (Click to expand)</summary>

```
+---------------------------------------------------------------------+
|                      FIRST-TIME SETUP (Run Once)                    |
+---------------------------------------------------------------------+
|                                                                     |
|  install.bat (Windows)                                              |
|      |                                                              |
|      +-- Check/Install WSL2                                         |
|      +-- Check/Install Ubuntu                                       |
|                                                                     |
|  first_setup.sh (run manually in Ubuntu/WSL)                        |
|      |                                                              |
|      +-- Check/Install tmux                                         |
|      +-- Check/Install Node.js v20+ (via nvm)                      |
|      +-- Check/Install Claude Code CLI                              |
|      +-- Configure Memory MCP server                                |
|                                                                     |
+---------------------------------------------------------------------+
|                      DAILY STARTUP (Run Every Day)                  |
+---------------------------------------------------------------------+
|                                                                     |
|  shutsujin_departure.sh                                             |
|      |                                                              |
|      +-> Create tmux sessions                                       |
|      |         - "oyabun" session (1 pane)                          |
|      |         - "multiagent" session (5 panes)                     |
|      |                                                              |
|      +-> Reset queue files and dashboard                            |
|      |                                                              |
|      +-> Launch Claude Code on all agents                           |
|                                                                     |
+---------------------------------------------------------------------+
```

</details>

<details>
<summary><b>shutsujin_departure.sh Options</b> (Click to expand)</summary>

```bash
# Default: Full startup (tmux sessions + Claude Code launch)
./shutsujin_departure.sh

# Session setup only (without launching Claude Code)
./shutsujin_departure.sh -s

# Full startup + open Windows Terminal tabs
./shutsujin_departure.sh -t

# Show help
./shutsujin_departure.sh -h
```

</details>

<details>
<summary><b>Common Workflows</b> (Click to expand)</summary>

**Normal Daily Usage:**
```bash
./shutsujin_departure.sh          # Start everything
tmux attach-session -t oyabun     # Connect to give commands
```

**Debug Mode (manual control):**
```bash
./shutsujin_departure.sh -s       # Create sessions only

# Manually start Claude Code on specific agents
tmux send-keys -t oyabun:0 'claude --dangerously-skip-permissions' Enter
tmux send-keys -t multiagent:0.0 'claude --dangerously-skip-permissions' Enter
```

**Restart After Crash:**
```bash
# Kill existing sessions
tmux kill-session -t oyabun
tmux kill-session -t multiagent

# Start fresh
./shutsujin_departure.sh
```

</details>

---

## File Structure

<details>
<summary><b>Click to expand file structure</b></summary>

```
neko-multi-agent/
|
|  +------------------- SETUP SCRIPTS -------------------+
+-- install.bat               # Windows: First-time setup
+-- first_setup.sh            # Ubuntu/Mac: First-time setup
+-- shutsujin_departure.sh    # Daily startup (auto-loads instructions)
|  +-----------------------------------------------------+
|
+-- instructions/             # Agent instruction files
|   +-- oyabun.md             # Boss Cat instructions
|   +-- bantou.md             # Foreman Cat instructions
|   +-- 1gou-neko.md          # Worker Cat #1 instructions
|   +-- 2gou-inu.md           # Worker Dog #2 instructions
|   +-- 3gou-neko.md          # Worker Cat #3 instructions
|   +-- 4gou-neko.md          # Worker Cat #4 instructions
|
+-- config/
|   +-- settings.yaml         # Language and other settings
|
+-- queue/                    # Communication files
|   +-- oyabun_to_bantou.yaml # Commands from Oyabun to Bantou
|   +-- tasks/                # Individual worker task files
|   +-- reports/              # Worker reports
|
+-- memory/                   # Memory MCP + learning patterns
+-- dashboard.md              # Real-time status overview
+-- CLAUDE.md                 # Project context for Claude
```

</details>

---

## Troubleshooting

<details>
<summary><b>MCP tools not working?</b></summary>

MCP tools are "deferred" and need to be loaded first:

```
# Wrong - tool not loaded
mcp__memory__read_graph()  <- Error!

# Correct - load first
ToolSearch("select:mcp__memory__read_graph")
mcp__memory__read_graph()  <- Works!
```

</details>

<details>
<summary><b>Agents asking for permissions?</b></summary>

Make sure to start with `--dangerously-skip-permissions`:

```bash
claude --dangerously-skip-permissions
```

</details>

<details>
<summary><b>Workers stuck?</b></summary>

Check the worker's pane:
```bash
tmux attach-session -t multiagent
# Use Ctrl+B then q to see pane numbers, then select
```

</details>

---

## tmux Quick Reference

| Command | Description |
|---------|-------------|
| `tmux attach -t oyabun` | Connect to Oyabun (Boss Cat) |
| `tmux attach -t multiagent` | Connect to workers |
| `Ctrl+B` then `q` then `0-4` | Switch between panes |
| `Ctrl+B` then `d` | Detach (leave running) |
| `tmux kill-session -t oyabun` | Stop Oyabun session |
| `tmux kill-session -t multiagent` | Stop worker sessions |

---

## Credits

Based on [Claude-Code-Communication](https://github.com/Akira-Papa/Claude-Code-Communication) by Akira-Papa.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

<div align="center">

**Command your cat team. Build faster.**

</div>
