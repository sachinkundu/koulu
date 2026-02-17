---
name: deploy-status
description: Check GitHub Actions CI status and Railway deployment status for the latest commit
user_invocable: true
model: haiku
---

# Deploy Status

Check CI and deployment status after pushing to main. Read-only — never triggers deploys or re-runs.

## Usage

```
/deploy-status
```

## Steps

### 1. Get Current Commit

Run in parallel:

```bash
git rev-parse HEAD
git log --oneline -1
```

Save the full SHA as `<sha>` and display the short commit info.

### 2. Check GitHub CI

```bash
gh run list --commit <sha> --json status,conclusion,name,url,databaseId --limit 5
```

**If no runs found:** Report "No CI runs found for this commit yet" and stop.

**If any job has `status: in_progress`:**
- Show which jobs are still running.
- Poll with `gh run watch <databaseId>` to wait for completion, then re-check.

**If any job has `conclusion: failure`:**
- Report which jobs failed with their URLs.
- Suggest: `gh run view <databaseId> --log-failed` to see failure details.
- **Stop here** — do not check Railway.

**If all jobs have `conclusion: success`:**
- Report all jobs passed.
- Proceed to Railway check.

### 3. Check Railway Deployment

First check if Railway CLI is available and project is linked:

```bash
railway status
```

**If `railway` not found or project not linked:** Warn user ("Railway CLI not installed" or "Run `railway link` to connect project") and skip this step.

**If linked:**

```bash
railway logs --limit 5
```

Check the most recent deployment status. Report the state (SUCCESS, BUILDING, DEPLOYING, FAILED, CRASHED, etc.).

### 4. Output Summary

Print a concise status block:

```
Commit: abc1234 feat(community): add member search
CI:      ✅ All 3 jobs passed
Railway: ✅ Deployed successfully
```

Adapt icons based on status:
- ✅ = success/deployed
- ⏳ = in progress/building
- ❌ = failed/crashed
- ⚠️ = unknown/not linked

## Rules

- **Read-only** — never trigger deploys, re-run CI jobs, or modify anything
- Assumes `gh` CLI is authenticated (it should be in this project)
- If Railway is not linked, report it and skip — do not attempt to link
- Use `haiku` model — this is a lightweight status check, no code generation
- Do not offer to fix failures — just report them clearly
