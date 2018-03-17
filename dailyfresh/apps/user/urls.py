from django.conf.urls import url
from apps.user import views
from django.contrib.auth.decorators import login_required
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView, LogoutView

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'), # 注册
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'), # 激活
    url(r'^login$', LoginView.as_view(), name='login'), # 登陆
    url(r'^logout$', LogoutView.as_view(), name='logout'), # 退出

# '''---用户中心页面---'''
    url(r'^$', UserInfoView.as_view(), name='user'), # 用户中心--信息页
    url(r'^order$', UserOrderView.as_view(), name='order'), # 用户中心--订单页
    url(r'^address$', UserSiteView.as_view(), name='address'), # 用户中心--收货地址页
]
