#!/bin/bash
# vergleich.sh a.tsv b.tsv : A ohne Kanon-Spalten (Q: 6., K: 6.), B ohne S-Zeilen
a=$1; b=$2
awk -F'\t' 'BEGIN{OFS="\t"} $1=="Q"{NF=5} $1=="K"{NF=5} {print}' "$a" | LC_ALL=C sort > ${TMPDIR:-/tmp}/va.tsv
grep -v '^S' "$b" | LC_ALL=C sort > ${TMPDIR:-/tmp}/vb.tsv
if cmp -s ${TMPDIR:-/tmp}/va.tsv ${TMPDIR:-/tmp}/vb.tsv; then echo "GLEICH ($(wc -l < ${TMPDIR:-/tmp}/va.tsv) Zeilen)"; else echo "VERSCHIEDEN"; diff ${TMPDIR:-/tmp}/va.tsv ${TMPDIR:-/tmp}/vb.tsv | head -20; fi
