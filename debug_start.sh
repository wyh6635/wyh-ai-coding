#!/bin/bash
echo "=== 诊断脚本 ==="
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "1. 检查 esbuild..."
node -e "const esbuild = require('$FRONTEND_DIR/node_modules/esbuild'); console.log('esbuild OK')" 2>&1 || echo "esbuild 检查失败"

echo ""
echo "2. 检查 sass..."
cd "$FRONTEND_DIR" && node -e "const sass = require('sass'); console.log('sass OK')" 2>&1 || echo "sass 检查失败"

echo ""
echo "3. 检查 node 版本..."
node --version

echo ""
echo "4. 检查 npm 版本..."
npm --version

echo ""
echo "5. 检查 Python 后端..."
cd "$BACKEND_DIR" && python -c "import fastapi; print('FastAPI OK')" 2>&1 || echo "FastAPI 检查失败"

echo ""
echo "6. 检查端口占用..."
lsof -i :5173 -i :8000 2>/dev/null || echo "无服务占用端口"

echo ""
echo "=== 诊断完成 ==="