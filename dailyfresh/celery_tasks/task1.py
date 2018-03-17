# 导入Celery类
from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

# 初始化django运行所依赖的环境变量
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")


# 创建Celery类的对象
app = Celery('celery_tasks.tasks', broker='redis://192.168.235.131:6379/3')



# 封装任务函数
@app.task
def send_register_active_email():
   print("该函数正在执行......")
   msg = '<h1>欢迎您成为天天生鲜注册会员</h1>'

   send_mail('验证信息', '', settings.EMAIL_FROM, ['sunrise9603@163.com'], html_message=msg)