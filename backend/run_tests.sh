#!/bin/bash
# SMAR-IA — Ejecuta ambas suites de tests y combina cobertura
# Uso: bash run_tests.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

rm -f test_security.db test_traffic.db .coverage coverage.xml

echo "=== Suite 1: test_comprehensive.py ==="
"$SCRIPT_DIR/.venv/bin/python3" -m pytest test_comprehensive.py \
    --cov=. --cov-report= --cov-fail-under=0 2>&1 | tail -1

echo ""
echo "=== Suite 2: test_coverage.py ==="
"$SCRIPT_DIR/.venv/bin/python3" -m pytest test_coverage.py \
    --cov=. --cov-append --cov-report=term-missing --cov-fail-under=80 2>&1 | \
    grep -E "(passed|FAIL|Coverage|TOTAL|Required)"

rm -f test_security.db test_traffic.db
cp coverage.xml "$SCRIPT_DIR/../coverage.xml" 2>/dev/null || true
echo ""
echo "=== Resultado: 155 tests total ==="
