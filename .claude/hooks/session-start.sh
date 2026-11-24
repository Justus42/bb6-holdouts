#!/bin/bash
# dockerd starten, falls er nicht laeuft. Zieht keine Images (das macht das Setup-Skript der Umgebung).
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
docker info >/dev/null 2>&1 && exit 0
command -v dockerd >/dev/null || { echo "session-start: dockerd fehlt" >&2; exit 0; }
setsid nohup dockerd >/tmp/dockerd.log 2>&1 < /dev/null &
for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && exit 0; sleep 1; done
echo "session-start: dockerd nach 30 s nicht bereit, siehe /tmp/dockerd.log" >&2
exit 0
