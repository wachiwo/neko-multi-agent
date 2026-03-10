# Kashira Unresponsive Escalation

Workers can escalate to oyabun when kashira appears down. This is a **confirmation request only** — workers do NOT restart kashira or take over any management duties.

## Escalation Conditions (both must be true)

1. Complete normal Task Completion Protocol (STEP 1-3: report YAML → inbox → send-keys)
2. Wait **5 minutes**. Check kashira pane:
   ```bash
   tmux capture-pane -t multiagent:0.0 -p | tail -5
   ```
3. If kashira shows **busy indicators** (no `❯` prompt, tool calls visible) → extend wait another 5 minutes
4. If kashira appears **idle** (`❯` prompt visible) but has **NOT processed your report** → escalate

## Escalation Procedure

1. Log to oyabun inbox:
   ```bash
   echo "$(date +%Y-%m-%dT%H:%M:%S)|{{WORKER_ID}}|escalation|kashira_unresponsive|{{TASK_ID}}" >> queue/inbox/oyabun.queue
   ```
2. Send-keys to oyabun (2-call method):
   ```bash
   tmux send-keys -t oyabun:0.0 'kashira appears unresponsive. Report {{TASK_ID}} written but not processed after N minutes. Requesting confirmation.'
   ```
   ```bash
   tmux send-keys -t oyabun:0.0 Enter
   ```

## Rules

- Only escalate after **BOTH conditions** met: kashira idle appearance + 5min no response
- **Max 1 escalation per incident** — do not spam oyabun
- If kashira responds during the wait, **cancel escalation** — do not send
- After escalating, return to idle and wait for oyabun's instructions
