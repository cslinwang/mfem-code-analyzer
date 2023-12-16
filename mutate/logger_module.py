import os
import sys
import logging

class StreamToLogger(object):
    """
    一个简单的流对象，将其写入操作重定向到一个日志记录器。
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
            # 将信息同时输出到控制台
            if self.log_level <= logging.INFO:
                sys.__stdout__.write(line + '\n')

    def flush(self):
        pass

class LoggerSetup:
    """
    一个设置日志记录器的类。
    """
    def __init__(self, base_log_path, app_name='my_application'):
        self.base_log_path = base_log_path
        self.app_name = app_name
        self.setup_logger()
        self.redirect_stdout_stderr()

    def setup_logger(self):
        log_file_path = os.path.join(self.base_log_path, 'log.log')
        info_log_file_path = os.path.join(self.base_log_path, 'info.log')

        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        if os.path.exists(info_log_file_path):
            os.remove(info_log_file_path)

        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        all_levels_handler = logging.FileHandler(log_file_path)
        all_levels_handler.setLevel(logging.DEBUG)

        info_handler = logging.FileHandler(info_log_file_path)
        info_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        all_levels_handler.setFormatter(formatter)
        info_handler.setFormatter(formatter)

        self.logger.addHandler(all_levels_handler)
        self.logger.addHandler(info_handler)

    def redirect_stdout_stderr(self):
        sys.stdout = StreamToLogger(logging.getLogger(self.app_name), logging.DEBUG)
        sys.stderr = StreamToLogger(logging.getLogger(self.app_name), logging.ERROR)

    def info(self, message):
        self.logger.info(message)
        message = str(message)
        sys.__stdout__.write("INFO: " + message + '\n')

    def debug(self, message):
        self.logger.debug(message)
        sys.__stdout__.write("DEBUG: " + message + '\n')

# 初始化日志配置
log_setup = LoggerSetup('/root/mfem-code-analyzer/mutate')

def info(message):
    log_setup.info(message)

def debug(message):
    log_setup.debug(message)
