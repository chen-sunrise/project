"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm7kig@=xqq!ps8pa&c8vf@*n8y&=zh!)vs7=impp23pby&i6f^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',  # 富文本编辑器
    'haystack', # 全文检索框架
    'user',  # 用户模块
    'cart',  # 购物车模块
    'goods',  # 商品模块
    'order', # 订单模块
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'PORT': 3306,
        'USER': 'dailyuser',
        'PASSWORD': 'dailyuser',
        'HOST': '192.168.235.131',
    }
}


# 指定django认证系统使用的用户模型类
AUTH_USER_MODEL = 'user.User'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# 配置静态文件路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 添加富文件编辑器配置
TINYMCE_DEFAUTL_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400,
}


# 发送邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = 'sunrise9603@163.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'sunrise9603'
#收件人看到的发件人
EMAIL_FROM = 'dailyfresh<sunrise9603@163.com>'

# Django框架中缓存配置
CACHES = {
  "default": {
      "BACKEND": "django_redis.cache.RedisCache",
      # 设置缓存信息存储到redis中
      "LOCATION": "redis://192.168.235.131:6379/4",
      "OPTIONS": {
          "CLIENT_CLASS": "django_redis.client.DefaultClient",
      }
  }
}
# Django框架中的session存储配置
# 设置session存储到缓存中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# session存储到CACHES配置项中default对应的redis数据库中
SESSION_CACHE_ALIAS = "default"


# 指定登陆页面的url地址
LOGIN_URL = '/user/login'


# 指定Django保存文件使用的文件存储类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDFSStorage'

# 指定FDFS客户端配置文件的路径
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fdfs/client.conf')

# 指定FDFS系统中Nginx的ip和port
FDFS_NGINX_URL = 'http://192.168.235.131:8888/'

# 全文检索框架配置
HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 索引文件路径
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'