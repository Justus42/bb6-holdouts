#!/usr/bin/env bash
# Programm 2 (unabhaengig von pr_abgleich.py): hinzugefuegte Zeilen jedes neuen/geaenderten
# busycoq-PRs (git diff, nur '+'-Zeilen) mit grep -F gegen alle Holdout-Strings (tm + aliases).
# Aufruf: bash pr_abgleich2.sh <bare-repo> <holdouts.json> [ziel_n,...]
# Ausgabe je PR: Nummer und Liste der getroffenen n; danach Ziel-Treffer ueber den GANZEN Baum
# (git grep) jedes PR-Kopfs, abzueglich der Treffer im BB6-Stand.
set -euo pipefail
repo=$1; json=$2; ziel=${3:-88,312,396,449,114,367,378,318,518,322,274}
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
jq -r '.holdouts[] | .n as $n | ([.tm] + [.aliases[].tm])[] | "\(.)\t\($n)"' "$json" > "$tmp/map.tsv"
cut -f1 "$tmp/map.tsv" > "$tmp/str.txt"
jq -r '.busycoq.pr_snapshot[] | "\(.number) \(.head_sha)"' "$json" > "$tmp/snap.txt"
git -C "$repo" for-each-ref --format='%(refname:lstrip=2) %(objectname)' refs/pr | sort -n > "$tmp/refs.txt"
gesamt=$(mktemp -p "$tmp")
while read -r n sha; do
  if grep -qx "$n $sha" "$tmp/snap.txt"; then continue; fi
  base=$(git -C "$repo" merge-base refs/heads/BB6 "$sha")
  hits=$(git -C "$repo" diff --no-renames "$base" "$sha" | { grep '^+' || true; } | { grep -oFf "$tmp/str.txt" || true; } | sort -u \
         | awk -F'\t' 'NR==FNR{m[$1]=$2;next}{print m[$1]}' "$tmp/map.tsv" - | sort -nu | tr '\n' ' ' || true)
  echo "PR $n: ${hits:--}"
  for h in $hits; do echo "$h"; done >> "$gesamt"
done < "$tmp/refs.txt"
echo "verschiedene Holdouts in neuen PRs: $(sort -nu "$gesamt" | wc -l)"
echo "--- Zielmaschinen, ganzer Baum je PR-Kopf (Treffer ausserhalb BB6) ---"
IFS=, read -ra Z <<< "$ziel"
for z in "${Z[@]}"; do
  awk -F'\t' -v z="$z" '$2==z{print $1}' "$tmp/map.tsv" > "$tmp/z.txt"
  b=$(git -C "$repo" grep -lFf "$tmp/z.txt" refs/heads/BB6 2>/dev/null | sed 's/^[^:]*://' | sort -u || true)
  neu=""
  while read -r n sha; do
    f=$(git -C "$repo" grep -lFf "$tmp/z.txt" "$sha" 2>/dev/null | sed 's/^[^:]*://' | sort -u || true)
    extra=$(comm -13 <(echo "$b") <(echo "$f") | grep -v '^$' || true)
    [ -n "$extra" ] && neu="$neu PR$n[$(echo $extra | tr ' ' ',')]"
  done < "$tmp/refs.txt"
  echo "n=$z: BB6-Dateien=$(echo "$b" | grep -c . || true) zusaetzlich:${neu:- keine}"
done
