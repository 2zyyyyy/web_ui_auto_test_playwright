import os
import sys
from loguru import logger
from config import config

# 创建日志目录
log_dir = os.path.dirname(config["log_file"])
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO",
           format="<green>{time}</green> | <level>{level}</level> | {message}")
logger.add(config["log_file"], level="INFO", rotation="10MB", retention="7 days")

log = logger
