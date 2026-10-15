#!/bin/sh
# Genera el apéndice online: tablas desde los CSV + prosa -> apendice.md -> appendix.pdf
cd "$(dirname "$0")"
PY="$(git rev-parse --show-toplevel 2>/dev/null)/.venv/bin/python"
[ -x "$PY" ] || PY=python3
"$PY" generar.py
pandoc apendice.md -o appendix.docx
soffice --headless --convert-to pdf appendix.docx --outdir . >/dev/null 2>&1
mv appendix.pdf ../appendix.pdf 2>/dev/null
ls -la apendice.md appendix.docx ../appendix.pdf 2>/dev/null
