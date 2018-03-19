'''login_required
1.验证用户是否登录
2.如果用户未登录则跳转到settings.LOGIN_URL指定的地址，
同时把访问的url通过next参数通过next参数跟在LONG_URL地址后面
3.如果用户已经登录，则调用对应的视图
 '''
from django.contrib.auth.decorators import login_required
from django.views.generic import View

'''
使用:
  1）方式1: 在进行url配置时，手动调用login_required装饰器。
  2）方式2:
    2.1 定义一个类LoginRequiredView, 继承View。
    2.2 重写as_view, 在重写的as_view方法中调用login_required实现登录验证。
    2.3 需要登录验证的类视图直接继承LoginRequiredView。
'''


# 方式2
class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        # 继承View中的as_view方法
        view = super().as_view(**initkwargs)

        # 登陆验证
        return login_required(view)


# 方式3  推荐使用
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)

        return login_required(view)
