#!/usr/bin/env sh
set -e

TARGET=$1

echo "Executando Black"
black -q "$TARGET"
echo "Executando Isort"
isort -q "$TARGET"
echo "Executando Flake8"
flake8 --ignore=E211,E999,F821,W503,E203 --max-line-length=121 --exclude=migrations,settings,__pycache__,tests,'URLs e Endpoints.py' "$TARGET"

# Corrige dono dos arquivos alterados
if [ -n "$HOST_UID" ] && [ -n "$HOST_GID" ]; then
    echo "Corrigindo dono dos arquivos..."
    chown -R "$HOST_UID:$HOST_GID" "$TARGET"
fi

echo "Fim"
