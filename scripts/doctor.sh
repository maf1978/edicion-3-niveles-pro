#!/bin/bash
# doctor.sh — revisa que tengas todo para editar con los 3 niveles PRO y dice cómo arreglar lo que falte.
# Uso:  bash doctor.sh          -> solo diagnóstico
#       bash doctor.sh --fix    -> instala lo que se puede instalar solo (HyperFrames, faster-whisper, numpy)
FIX=false; [ "$1" = "--fix" ] && FIX=true
OK=true
say()  { printf "  %s %s\n" "$1" "$2"; }
need() { OK=false; say "❌" "$1"; printf "     → %s\n" "$2"; }

echo "── edicion-3-niveles-pro · doctor ──────────────────────"

if command -v python3 >/dev/null; then say "✅" "python3 $(python3 -V 2>&1 | cut -d' ' -f2)"
else need "python3 no encontrado" "instala Python 3.10+: https://www.python.org/downloads/ (mac: brew install python)"; fi

if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then say "✅" "ffmpeg $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3)"
else need "ffmpeg no encontrado" "mac: brew install ffmpeg · ubuntu: sudo apt install ffmpeg · windows: winget install ffmpeg"; fi

if command -v node >/dev/null; then
  NODEV=$(node -v | sed 's/v//' | cut -d. -f1)
  if [ "$NODEV" -ge 22 ] 2>/dev/null; then say "✅" "node $(node -v)"
  else need "node $(node -v) es viejo (HyperFrames pide 22 o más)" "mac: brew install node · o con nvm: nvm install 22"; fi
else need "node no encontrado (HyperFrames lo necesita)" "mac: brew install node · windows: winget install OpenJS.NodeJS.LTS · linux: nvm install 22"; fi

if command -v node >/dev/null; then
  if npx --no-install hyperframes --version >/dev/null 2>&1 || npm ls -g hyperframes >/dev/null 2>&1; then say "✅" "HyperFrames CLI"
  elif $FIX; then echo "  ⏳ instalando HyperFrames…"; npm install -g hyperframes >/dev/null 2>&1 && say "✅" "HyperFrames instalado" || need "HyperFrames" "npm install -g hyperframes"
  else need "HyperFrames no instalado" "npm install -g hyperframes   (o: bash doctor.sh --fix)"; fi
fi

if python3 -c "import numpy" 2>/dev/null; then say "✅" "numpy (detección de silencios rápida)"
elif $FIX; then python3 -m pip install --quiet numpy && say "✅" "numpy instalado" || say "⚠️ " "numpy no se instaló (cortar.py funciona igual, más lento)"
else say "⚠️ " "numpy no instalado (opcional, acelera cortar.py): python3 -m pip install numpy"; fi

# Transcripción: AssemblyAI si hay llave; si no, Whisper local
if [ -n "$ASSEMBLYAI_API_KEY" ] || [ -s "$HOME/.config/assemblyai/key" ]; then
  say "✅" "AssemblyAI (llave encontrada): transcripción más precisa"
else
  say "ℹ️ " "Sin llave de AssemblyAI: se usará Whisper local (gratis). Para más precisión: cuenta gratis en assemblyai.com y guarda la llave en ~/.config/assemblyai/key"
  if python3 -c "import faster_whisper" 2>/dev/null; then say "✅" "Whisper local (faster-whisper)"
  elif $FIX; then echo "  ⏳ instalando faster-whisper…"; python3 -m pip install --quiet faster-whisper && say "✅" "faster-whisper instalado" || need "faster-whisper" "python3 -m pip install faster-whisper"
  else need "Whisper local no instalado" "python3 -m pip install faster-whisper   (o: bash doctor.sh --fix)"; fi
fi

# Recorte con IA local (texto detrás de ti)
if command -v node >/dev/null && npx --no-install hyperframes remove-background --info >/dev/null 2>&1; then
  PROV=$(npx --no-install hyperframes remove-background --info 2>/dev/null | grep -i "Auto-selected" | awk '{print $NF}')
  say "✅" "recorte de persona con IA local (${PROV:-cpu})"
  [ "$PROV" = "cpu" ] && say "ℹ️ " "sin GPU el recorte va lento (~2-3 cuadros/s): úsalo en clips cortos o en el hook"
else say "⚠️ " "recorte de persona no disponible (actualiza HyperFrames: npm install -g hyperframes@latest)"; fi

if [ -s "$HOME/.config/edicion-3-niveles-pro/estilo.json" ]; then say "✅" "tu estilo activo (~/.config/edicion-3-niveles-pro/estilo.json)"
  N=$(ls "$HOME/.config/edicion-3-niveles-pro/estilos" 2>/dev/null | wc -l | tr -d ' '); say "ℹ️ " "estilos en tu biblioteca: $N"
elif [ -s "$HOME/.config/edicion-3-niveles/estilo.json" ]; then say "ℹ️ " "tienes el estilo del skill gratis: lo migro al pro en el setup"
else say "ℹ️ " "todavía no hay estilo: Claude te hace el setup avanzado la primera vez"; fi

echo "────────────────────────────────────────────────────"
$OK && echo "Todo listo ✨" || { echo "Falta algo. Pégale este resultado a Claude Code y dile: ayúdame a arreglarlo"; exit 1; }
