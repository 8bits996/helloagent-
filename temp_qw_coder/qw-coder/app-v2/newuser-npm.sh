echo 'export PATH=/codev/opt/nodejs/20.10.0/bin:$PATH' >> ~/.bashrc
echo 'export PATH=~/.npm/node_modules/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g --registry=https://mirrors.tencent.com/npm @tencent/claude-code-internal

# 测试方法： claude-internal --dangerously-skip-permissions -p helloworld
# claude-internal --dangerously-skip-permissions -p "用工蜂mcp获取下gpt-demo仓库的MR
