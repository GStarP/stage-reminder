import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    配置并返回一个全局的logger实例
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    # 创建logger实例
    logger = logging.getLogger('StageReminder')
    logger.setLevel(logging.INFO)  # 设置最低日志级别

    # 如果logger已经有处理器，说明已经初始化过，直接返回
    if logger.handlers:
        return logger

    # 创建logs目录（如果不存在）
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置文件处理器
    log_file = os.path.join(log_dir, 'stagereminder.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,          # 保留5个备份文件
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    # 配置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 将格式化器添加到处理器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 创建全局logger实例
logger = setup_logger()