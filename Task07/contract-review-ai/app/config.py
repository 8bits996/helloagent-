"""
配置管理
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # CodeBuddy配置
    CODEBUDDY_API_URL: str = "http://127.0.0.1:3000"
    
    # FastAPI配置
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    
    # Streamlit配置
    STREAMLIT_PORT: int = 8508
    
    # 文件存储路径
    DATA_DIR: Path = Path("data")
    UPLOAD_DIR: Path = Path("data/uploads")
    OUTPUT_DIR: Path = Path("data/outputs")
    KB_DIR: Path = Path("知识库")
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/contract_review.db"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/app.log")
    
    # MarkItDown配置
    ENABLE_LLM_DESCRIPTION: bool = False

    # LLM配置 (OpenAI兼容)
    LLM_API_KEY: str = ""  # 请在.env文件中配置
    LLM_BASE_URL: str = "" # 请在.env文件中配置
    LLM_MODEL: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.KB_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
