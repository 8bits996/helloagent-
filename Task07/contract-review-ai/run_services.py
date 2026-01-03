"""
服务管理器 - 自动启动和监控 FastAPI + Streamlit 服务
支持自动重启、健康检查、日志记录

使用方法:
    python run_services.py          # 启动所有服务
    python run_services.py --check  # 仅检查服务状态
    python run_services.py --stop   # 停止所有服务
"""

import subprocess
import time
import sys
import os
import signal
import requests
import threading
import logging
import webbrowser
from datetime import datetime
from pathlib import Path

# 配置
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 8508
HEALTH_CHECK_INTERVAL = 60  # 健康检查间隔(秒) - 增加到60秒减少检查频率
MAX_RESTART_ATTEMPTS = 3    # 最大重启次数 - 减少到3次
RESTART_COOLDOWN = 180      # 重启冷却时间(秒) - 增加到3分钟
STARTUP_WAIT_TIME = 8       # 启动等待时间(秒)

# 日志配置
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "service_manager.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        self.backend_restart_count = 0
        self.frontend_restart_count = 0
        self.last_backend_restart = 0
        self.last_frontend_restart = 0
        self.restart_lock = threading.Lock()  # 重启互斥锁
        
        # 获取项目目录
        self.project_dir = Path(__file__).parent.absolute()
        
    def check_port_in_use(self, port):
        """检查端口是否被占用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
    
    def kill_process_on_port(self, port):
        """终止占用指定端口的进程"""
        try:
            # Windows
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        parts = line.split()
                        pid = parts[-1]
                        subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                        logger.info(f"已终止端口 {port} 上的进程 PID={pid}")
                        time.sleep(1)
        except Exception as e:
            logger.warning(f"终止端口 {port} 进程失败: {e}")
    
    def start_backend(self):
        """启动后端服务"""
        if self.check_port_in_use(BACKEND_PORT):
            logger.warning(f"端口 {BACKEND_PORT} 已被占用，尝试终止...")
            self.kill_process_on_port(BACKEND_PORT)
            time.sleep(3)
        
        logger.info("正在启动 FastAPI 后端服务...")
        
        # 使用单 worker 模式，避免多进程共享状态问题
        # 增加超时和连接限制参数
        self.backend_process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", BACKEND_HOST,
                "--port", str(BACKEND_PORT),
                "--workers", "1",              # 单进程模式，更稳定
                "--limit-concurrency", "50",   # 限制并发连接数
                "--timeout-keep-alive", "60",  # 保持连接超时
                "--timeout-graceful-shutdown", "10",  # 优雅关闭超时
                "--log-level", "info"          # 保留 info 日志便于调试
            ],
            cwd=str(self.project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # 等待启动
        time.sleep(STARTUP_WAIT_TIME)
        
        if self.check_backend_health():
            logger.info(f"✅ 后端服务启动成功: http://{BACKEND_HOST}:{BACKEND_PORT}")
            return True
        else:
            logger.error("❌ 后端服务启动失败")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        if self.check_port_in_use(FRONTEND_PORT):
            logger.warning(f"端口 {FRONTEND_PORT} 已被占用，尝试终止...")
            self.kill_process_on_port(FRONTEND_PORT)
            time.sleep(2)
        
        logger.info("正在启动 Streamlit 前端服务...")
        
        # 增加 Streamlit 配置参数提高稳定性
        self.frontend_process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run",
                "app/frontend.py",
                "--server.port", str(FRONTEND_PORT),
                "--server.headless", "true",
                "--server.runOnSave", "false",
                "--server.fileWatcherType", "none",      # 禁用文件监视，减少资源占用
                "--server.maxUploadSize", "200",         # 最大上传文件大小 200MB
                "--browser.gatherUsageStats", "false",
                "--client.showErrorDetails", "false"     # 隐藏详细错误
            ],
            cwd=str(self.project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # 等待启动
        time.sleep(STARTUP_WAIT_TIME)
        
        if self.check_frontend_health():
            logger.info(f"✅ 前端服务启动成功: http://localhost:{FRONTEND_PORT}")
            return True
        else:
            logger.error("❌ 前端服务启动失败")
            return False
    
    def check_backend_health(self):
        """检查后端健康状态（带多次重试）"""
        for attempt in range(3):
            try:
                response = requests.get(
                    f"http://{BACKEND_HOST}:{BACKEND_PORT}/health",
                    timeout=10  # 增加超时时间
                )
                return response.status_code == 200
            except requests.exceptions.ConnectionError:
                if attempt < 2:
                    time.sleep(2)  # 增加重试间隔
                    continue
                return False
            except Exception:
                return False
        return False
    
    def check_frontend_health(self):
        """检查前端健康状态"""
        try:
            response = requests.get(
                f"http://localhost:{FRONTEND_PORT}/_stcore/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            # Streamlit 可能没有 health 端点，检查端口
            return self.check_port_in_use(FRONTEND_PORT)
    
    def restart_backend(self):
        """重启后端服务"""
        with self.restart_lock:  # 加锁防止并发重启
            current_time = time.time()
            
            # 检查冷却时间
            if current_time - self.last_backend_restart < RESTART_COOLDOWN:
                logger.warning("后端重启冷却中，跳过...")
                return False
            
            # 检查重启次数
            if self.backend_restart_count >= MAX_RESTART_ATTEMPTS:
                logger.error(f"后端重启次数已达上限 ({MAX_RESTART_ATTEMPTS})，停止重启")
                return False
            
            logger.warning("后端服务异常，正在重启...")
            
            # 终止现有进程
            if self.backend_process:
                try:
                    self.backend_process.terminate()
                    self.backend_process.wait(timeout=5)
                except:
                    try:
                        self.backend_process.kill()
                    except:
                        pass
            
            self.kill_process_on_port(BACKEND_PORT)
            time.sleep(3)
            
            # 重新启动
            success = self.start_backend()
            
            self.backend_restart_count += 1
            self.last_backend_restart = current_time
            
            if success:
                logger.info(f"后端服务重启成功 (第 {self.backend_restart_count} 次)")
            
            return success
    
    def restart_frontend(self):
        """重启前端服务"""
        current_time = time.time()
        
        if current_time - self.last_frontend_restart < RESTART_COOLDOWN:
            logger.warning("前端重启冷却中，跳过...")
            return False
        
        if self.frontend_restart_count >= MAX_RESTART_ATTEMPTS:
            logger.error(f"前端重启次数已达上限 ({MAX_RESTART_ATTEMPTS})，停止重启")
            return False
        
        logger.warning("前端服务异常，正在重启...")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                self.frontend_process.kill()
        
        self.kill_process_on_port(FRONTEND_PORT)
        time.sleep(2)
        
        success = self.start_frontend()
        
        self.frontend_restart_count += 1
        self.last_frontend_restart = current_time
        
        if success:
            logger.info(f"前端服务重启成功 (第 {self.frontend_restart_count} 次)")
        
        return success
    
    def health_check_loop(self):
        """健康检查循环（优化版）"""
        consecutive_failures = {"backend": 0, "frontend": 0}
        check_count = 0
        
        while self.running:
            time.sleep(HEALTH_CHECK_INTERVAL)
            
            if not self.running:
                break
            
            check_count += 1
            
            # 检查后端
            backend_ok = self.check_backend_health()
            if not backend_ok:
                consecutive_failures["backend"] += 1
                logger.warning(f"后端健康检查失败 ({consecutive_failures['backend']}/5)")
                
                # 连续失败5次才重启
                if consecutive_failures["backend"] >= 5:
                    logger.error("后端连续5次健康检查失败，尝试重启...")
                    self.restart_backend()
                    consecutive_failures["backend"] = 0
            else:
                if consecutive_failures["backend"] > 0:
                    logger.info("后端服务已恢复正常")
                consecutive_failures["backend"] = 0
            
            # 检查前端
            frontend_ok = self.check_frontend_health()
            if not frontend_ok:
                consecutive_failures["frontend"] += 1
                logger.warning(f"前端健康检查失败 ({consecutive_failures['frontend']}/5)")
                
                if consecutive_failures["frontend"] >= 5:
                    logger.error("前端连续5次健康检查失败，尝试重启...")
                    self.restart_frontend()
                    consecutive_failures["frontend"] = 0
            else:
                if consecutive_failures["frontend"] > 0:
                    logger.info("前端服务已恢复正常")
                consecutive_failures["frontend"] = 0
            
            # 每10次检查输出一次状态日志
            if check_count % 10 == 0:
                logger.info(f"服务运行正常 (已运行 {check_count * HEALTH_CHECK_INTERVAL // 60} 分钟)")
    
    def start_all(self):
        """启动所有服务"""
        logger.info("=" * 60)
        logger.info("合同评审AI系统 - 服务管理器启动")
        logger.info("=" * 60)
        
        # 启动后端
        if not self.start_backend():
            logger.error("后端启动失败，退出")
            return False
        
        # 启动前端
        if not self.start_frontend():
            logger.error("前端启动失败，退出")
            return False
        
        self.running = True
        
        # 启动健康检查线程
        health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        health_thread.start()
        
        logger.info("=" * 60)
        logger.info("所有服务已启动")
        logger.info(f"  后端 API: http://{BACKEND_HOST}:{BACKEND_PORT}")
        logger.info(f"  API 文档: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
        logger.info(f"  前端界面: http://localhost:{FRONTEND_PORT}")
        logger.info("=" * 60)
        logger.info("按 Ctrl+C 停止服务...")
        
        # 自动打开浏览器
        try:
            webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
            logger.info("已自动打开浏览器")
        except Exception as e:
            logger.warning(f"无法自动打开浏览器: {e}")
        
        return True
    
    def stop_all(self):
        """停止所有服务"""
        logger.info("正在停止所有服务...")
        self.running = False
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
            logger.info("后端服务已停止")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                self.frontend_process.kill()
            logger.info("前端服务已停止")
        
        # 确保端口释放
        self.kill_process_on_port(BACKEND_PORT)
        self.kill_process_on_port(FRONTEND_PORT)
        
        logger.info("所有服务已停止")
    
    def run(self):
        """运行服务管理器"""
        if not self.start_all():
            return
        
        try:
            # 主循环 - 监控进程状态
            while self.running:
                time.sleep(1)
                
                # 检查进程是否意外退出
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.warning("后端进程意外退出")
                    self.restart_backend()
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.warning("前端进程意外退出")
                    self.restart_frontend()
                    
        except KeyboardInterrupt:
            logger.info("收到停止信号...")
        finally:
            self.stop_all()
    
    def check_status(self):
        """检查服务状态"""
        print("\n" + "=" * 50)
        print("服务状态检查")
        print("=" * 50)
        
        # 后端状态
        backend_ok = self.check_backend_health()
        print(f"\n后端服务 (:{BACKEND_PORT}): ", end="")
        if backend_ok:
            print("✅ 运行中")
        else:
            print("❌ 未运行")
        
        # 前端状态
        frontend_ok = self.check_frontend_health()
        print(f"前端服务 (:{FRONTEND_PORT}): ", end="")
        if frontend_ok:
            print("✅ 运行中")
        else:
            print("❌ 未运行")
        
        print("\n" + "=" * 50)
        
        return backend_ok and frontend_ok


def main():
    manager = ServiceManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            manager.check_status()
        elif sys.argv[1] == "--stop":
            manager.kill_process_on_port(BACKEND_PORT)
            manager.kill_process_on_port(FRONTEND_PORT)
            print("服务已停止")
        else:
            print("用法:")
            print("  python run_services.py          # 启动所有服务")
            print("  python run_services.py --check  # 检查服务状态")
            print("  python run_services.py --stop   # 停止所有服务")
    else:
        manager.run()


if __name__ == "__main__":
    main()
