# Gunicorn配置文件

import multiprocessing

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "uvicorn.workers.UvicornWorker"

# 绑定地址
bind = "unix:/tmp/exam.sock"

# 超时时间
timeout = 30

# 访问日志
accesslog = "-"

# 错误日志
errorlog = "-"

# 日志级别
loglevel = "info"
