#!/usr/bin/env bash
set -euo pipefail

# Script de build para entornos como Render: instalar dependencias (si es necesario),
# aplicar migraciones y coleccionar estáticos.
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Build complete."
