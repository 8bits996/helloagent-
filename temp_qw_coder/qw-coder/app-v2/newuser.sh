# 创建用户,指定 shell 和添加到 wheel 组
useradd -m -s /bin/bash -G wheel admin1

# 设置密码
passwd admin1
