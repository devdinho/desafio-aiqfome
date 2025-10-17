#!/usr/bin/env sh

set -e

echo "Executando Black"
black -q --check --diff $1
echo "Executando Isort"
isort -q --check --diff "$1"
echo "Executando Flake8"
flake8 --ignore=E211,E999,F821,W503,E203 --max-line-length=121 --exclude=migrations,settings,__pycache__,tests $1
echo "✅ Verificação concluída"