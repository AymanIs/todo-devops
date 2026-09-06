#!/usr/bin/env bash
# Copie les hooks du depot vers .git/hooks
racine="$(git rev-parse --show-toplevel)"
cp "$racine/githooks/pre-commit" "$racine/.git/hooks/pre-commit"
cp "$racine/githooks/commit-msg" "$racine/.git/hooks/commit-msg"
chmod +x "$racine/.git/hooks/pre-commit" "$racine/.git/hooks/commit-msg"
echo "Hooks installes."
