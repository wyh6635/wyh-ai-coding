#!/bin/bash

echo "=== 校园信息管理系统 启动脚本 ==="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

setup_backend() {
    echo "[1/2] 配置后端服务..."
    cd "$BACKEND_DIR"
    pip install -r requirements.txt -q 2>/dev/null
    if [ $? -ne 0 ]; then
        pip install -r requirements.txt
    fi
    echo "  ✓ 后端依赖安装完成"
}

setup_frontend() {
    echo "[2/2] 配置前端服务..."
    cd "$FRONTEND_DIR"
    npm install 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  ✗ 前端依赖安装失败，请手动执行: cd frontend && npm install"
        return 1
    fi
    echo "  ✓ 前端依赖安装完成"
}

echo ""
echo "=== 开始环境配置 ==="
echo ""

setup_backend
setup_frontend

echo ""
echo "=== 启动服务 ==="
echo ""
echo "后端服务: cd backend && python main.py"
echo "前端服务: cd frontend && npm run dev"
echo ""
echo "后端 API: http://localhost:8000"
echo "前端页面: http://localhost:5173"
echo ""
echo "测试账号:"
echo "  管理员: admin / 123456"
echo "  学员:   student001 / 123456"
echo ""
echo "启动完成后请访问: http://localhost:5173"