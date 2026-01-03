#!/bin/bash
# ============================================================
# 漏洞修复脚本 - 三台母机批量修复
# ============================================================

# ============================================================
# 第一批：母机 21.91.168.209 (docker-web-1)
# 漏洞：Next.js 15.5.6, React 19.1.1, React-DOM 19.1.1
# ============================================================
echo "========== 开始修复母机 21.91.168.209 =========="
ssh root@21.91.168.209 << 'EOF'
echo ">>> 进入容器 docker-web-1 执行修复..."
docker exec docker-web-1 sh -c '
cd /app/web
echo "当前版本："
cat package.json | grep -E "next|react" | head -5
echo ">>> 升级 Next.js 和 React..."
npm install next@15.5.9 react@19.1.4 react-dom@19.1.4 --save
echo ">>> 重新构建..."
npm run build
echo ">>> 修复后版本："
cat node_modules/next/package.json | grep \"version\"
cat node_modules/react/package.json | grep \"version\"
cat node_modules/react-dom/package.json | grep \"version\"
'
echo ">>> 母机 21.91.168.209 修复完成"
EOF

# ============================================================
# 第二批：母机 21.91.237.241 (CodeV容器 frankechen-23h8wckd2a)
# 漏洞：dify的React/Next.js + n8n的pdfjs-dist
# ============================================================
echo "========== 开始修复母机 21.91.237.241 =========="
ssh root@frankechen-23h8wckd2a.devcloud.woa.com << 'EOF'
echo ">>> 修复 dify 项目..."
cd /data/workspace/dify/web
echo "当前版本："
cat package.json | grep -E "next|react" | head -5
npm install react@19.1.4 react-dom@19.1.4 next@15.5.9 --save
echo "修复后版本："
cat node_modules/next/package.json | grep \"version\" || echo "next not found"
cat node_modules/react/package.json | grep \"version\" || echo "react not found"

echo ">>> 修复 n8n 的 pdfjs-dist..."
# 全局 n8n
cd /usr/lib/node_modules/n8n 2>/dev/null && npm install pdfjs-dist@5.2.133 --save || echo "全局n8n路径不存在"
# 工作区 n8n
cd /data/workspace/n8n/n8n-workspace 2>/dev/null && npm install pdfjs-dist@5.2.133 --save || echo "工作区n8n路径不存在"
# 清理 npx 缓存
rm -rf /root/.npm/_npx/57cd747f8c45ea1d 2>/dev/null || true

echo ">>> 母机 21.91.237.241 修复完成"
EOF

# ============================================================
# 第三批：母机 21.6.237.240 (CodeV容器 frankechen-25m7nag5ka)
# 漏洞：codebuddy-cli的React + rss/dify的React/Next.js + n8n的pdfjs-dist
# ============================================================
echo "========== 开始修复母机 21.6.237.240 =========="
ssh root@frankechen-25m7nag5ka.devcloud.woa.com << 'EOF'
echo ">>> 修复 codebuddy-cli..."
npm install -g @tencent/codebuddy-cli --registry=https://mirrors.tencent.com/npm

echo ">>> 修复 rss/dify 项目..."
cd /data/workspace/rss/dify/web 2>/dev/null || cd /data/workspace/dify/web 2>/dev/null
if [ -f package.json ]; then
    echo "当前版本："
    cat package.json | grep -E "next|react" | head -5
    npm install react@19.1.4 react-dom@19.1.4 next@15.5.9 --save
    echo "修复后版本："
    cat node_modules/next/package.json | grep \"version\" || echo "next not found"
    cat node_modules/react/package.json | grep \"version\" || echo "react not found"
else
    echo "dify项目路径不存在，跳过"
fi

echo ">>> 修复 n8n 的 pdfjs-dist..."
cd /usr/local/lib/node_modules/n8n 2>/dev/null && npm install pdfjs-dist@5.2.133 --save || echo "全局n8n路径不存在"
cd /data/workspace/n8n 2>/dev/null && npm install pdfjs-dist@5.2.133 --save || echo "工作区n8n路径不存在"

echo ">>> 母机 21.6.237.240 修复完成"
EOF

echo "========== 所有母机修复完成 =========="
