#!/usr/bin/env bash
# Scriptzinho para automatizar: git add . + commit + pull --rebase + push

set -e  # se algum comando der erro, o script para

# Mensagem de commit vem do primeiro argumento, ou usa uma padrão
MSG="$1"
if [ -z "$MSG" ]; then
  MSG="Atualizações rápidas"
fi

echo "🔍 Status atual:"
git status

echo ""
echo "➕ Adicionando arquivos modificados..."
git add .

# Verifica se realmente tem algo staged para commit
if git diff --cached --quiet; then
  echo "⚠️ Nenhuma alteração para commitar. Saindo."
  exit 0
fi

echo ""
echo "💾 Criando commit: \"$MSG\""
git commit -m "$MSG"

echo ""
echo "⬇️ Atualizando com o remoto (git pull --rebase origin main)..."
git pull origin main --rebase

echo ""
echo "⬆️ Enviando para o GitHub (git push origin main)..."
git push origin main

echo ""
echo "✅ Tudo certo! Alterações enviadas para o GitHub."
