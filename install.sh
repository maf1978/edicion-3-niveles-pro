#!/bin/bash
# Instala o actualiza el skill en ~/.claude/skills/edicion-3-niveles-pro y revisa el entorno.
# Uso: curl -fsSL https://raw.githubusercontent.com/santmun/edicion-3-niveles-pro/main/install.sh | bash
set -e
DEST="$HOME/.claude/skills/edicion-3-niveles-pro"
REPO="https://github.com/santmun/edicion-3-niveles-pro"
mkdir -p "$HOME/.claude/skills"
if [ -d "$DEST/.git" ]; then
  echo "Actualizando edicion-3-niveles-pro…"; git -C "$DEST" pull --ff-only
else
  echo "Instalando edicion-3-niveles-pro…"; git clone --depth 1 "$REPO" "$DEST"
fi
bash "$DEST/scripts/doctor.sh" --fix || true
echo
echo "Listo. Abre Claude Code y dile: hazme el setup avanzado de mi estilo y edita mi primer video."
