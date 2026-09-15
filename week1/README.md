# Week 1 — Make Scripts Run Themselves

## What was built

- A Python script (hello_time.py) that logs the current time to a file
- Runs automatically daily on macOS via launchd
- Runs automatically daily in the cloud via GitHub Actions
- Detects its environment (GITHUB_ACTIONS env var) and writes to the appropriate log
- Cloud version auto-commits its output back to the repo ([skip ci])

## Files

| File | Purpose |
|------|---------|
| hello_time.py | The script — chooses local or cloud log based on environment |
| hello_time_local.log | Written by macOS launchd job |
| hello_time_cloud.log | Written by GitHub Actions, auto-committed |
| launchd/com.walid.hellotime.plist | macOS schedule config |

## Lessons learned

1. pathlib > strings — never build paths with + or os.path.join
2. __file__ not Path.home() — scripts must work anywhere
3. Environment detection — check GITHUB_ACTIONS to branch behavior
4. Logging levels — INFO for progress, exception() for errors with traceback
5. Exit codes — sys.exit(main()) for launchd to see success/failure
6. Secrets — never in code; GitHub Secrets or .env (gitignored)
7. Git discipline — status before add, before commit, after commit
8. One writer per file — split logs so Mac and cloud don't collide
9. [skip ci] — prevents workflows from infinite-looping on their own commits
10. Divergence happens — when bot commits while you commit, pull first

## Commands to remember

    # schedule (mac)
    launchctl load   ~/Library/LaunchAgents/com.walid.hellotime.plist
    launchctl list | grep hellotime
    launchctl start  com.walid.hellotime

    # actions
    gh run list --limit 5
    gh run view <ID> --log
    gh run view <ID> --log-failed
    gh run view <ID> --web
    gh workflow run hello.yml
