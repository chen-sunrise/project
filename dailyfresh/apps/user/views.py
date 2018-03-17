from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
import re
from user.models import User, Address
from django.http import HttpResponse
from django.core.mail import send_mail
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequiredMixin, LoginRequiredView

from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from goods.models import GoodsSKU

# Create your views here.


# /user/register
# get: 显示注册页面
# post: 进行注册处理
# request.method -> GET POST

'''def register_1(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

    # 判断信息是否完整
    if not all([username, password, email]):
        return render(request,  'register.html', {'errmsg': '信息不完整'})

    # 校验邮箱的格式
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式不对'})

    # 校验用户是否已注册
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user is not None:
        return render(request, 'register.html', {'errmsg': '该用户已被注册'})

    # 校验邮箱是否被注册

    # 3.业务处理：注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 注册之后，需要给用户的注册邮箱发送激活邮件，在激活邮箱中需要包含激活链接
    # 激活链接：/user/active/用户id
    # 存在问题：其他用户恶意请求网站进行用户激活操作
    # 解决问题：对用户的信息进行加密，八加密后的信息放在激活链接中，激活的时候进行解密
    # /user/active/加密后token信息

    # 4.返回应答：跳转到首页
    return redirect(reverse('goods:index'))'''


# 类视图
# /user/register
class RegisterView(View):
    '''注册界面'''
    # get请求方式
    def get(self, request):
        print('--get--')
        return render(request, 'register.html')

    # post请求方式
    def post(self, request):
        print('--post--')
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 通过后端判断数据完整性
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '信息不完整'})

        # 判断邮箱是否正确
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})


        # 判断该用户是否已被注册
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if not user is None:
            return render(request, 'register.html', {'errmsg': '该用户已被注册'})


        # 注册用户
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 注册之后，需要给用户的注册邮箱发送激活邮件，在激活邮箱中需要包含激活链接
        # 激活链接：/user/active/用户id
        # 存在问题：其他用户恶意请求网站进行用户激活操作
        # 解决问题：对用户的信息进行加密，八加密后的信息放在激活链接中，激活的时候进行解密


        # 对用户的身份信息进行加密，生成激活token信息
        # Serializer函数的参数  秘钥方式  时间（单位为秒）
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}

        # 返回bytes类型  对该用户进行密
        token = serializer.dumps(info)
        # str
        token =token.decode()

        # 组织邮件信息
        # subject = '激活验证信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # html_message = '''
        #      <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
        #     请点击一下链接激活您的账号(1小时之内有效)<br/>
        #     <a href="http://127.0.0.1:8000/user/active/%s">
        #     http://127.0.0.1:8000/user/active/%s</a>
        # '''% (username,token,token)
        #
        #
        # # 发送激活邮件
        # # send_mail(subject='邮件标题'
        # #             message = '邮件正文'
        # #             from_email='发件人'
        # #             recipient_list='收件人列表')
        # send_mail(subject, message, sender, receiver, html_message=html_message)

        # 利用celery来发送邮件
        # from celery_tasks.task2 import send_register_active_email
        from celery_tasks.tasks import send_register_active_email
        send_register_active_email.delay(email, username, token)


        # 跳转到首页
        return redirect(reverse('goods:index'))



# /user/active/加密token
class ActiveView(View):
    '''激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)

        try:
            # 解密
            info = serializer.loads(token)
            # 获取待激活的用户id
            user_id = info['confirm']
            # 激活用户
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已失败
            # 实际开发： 返回页面，让你点击链接再发激活邮件
            return HttpResponse('激活链接已失效')


# /user/login
class LoginView(View):
    '''登陆'''
    def get(self, request):
        '''显示'''
        # 判断是否记住用户名
        username = request.COOKIES.get('username')

        checked = 'checked'
        if username is None:
            # 没有记住用户名
            username = ''
            checked = ''


        return render(request, 'login.html')

    def post(self, request):
        '''登陆校验'''
        # 1.接收参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')

        # 2. 参数校验（后端校验）
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'信息不完整'})

        # 3. 业务处理：登陆校验 authenticate 是python提供的一个登陆校验函数
        user = authenticate(username=username, password= password)
        if user is not None:
            # 用户名和密码正确
            if user.is_active:
            # 用户已激活
            # 记住用户的登陆状态 login为python提供的记住登陆状态的函数
                login(request, user)

                # 获取用户登录之前访问的url地址，默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                response = redirect(next_url)

            # 判断是否记住用户名
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg':'用户未激活'})
        else:
            #  用户或密码错误
            return render(request, 'login.html', {'errmsg': '用户或密码错误'})


    '''
        request对象有一个属性user， request.user
        如果用户已登陆，request.user是一个认证用户模型类（User）的对象，包含登陆用户的信息
        如果用户为未登陆，request.user是一个匿名用户类（AnonymousUser）的对象

        is_authenticated
        User类这个方法永远返回的是Ture
        AnonymousUser类这个方法永远返回的是False

        在模板文件中可以直接使用一个模板变量user，实际上就是request.user
    '''

#/user/logout
class LogoutView(View):
    '''退出'''
    def get(self, request):
        '''退出'''
        # 清楚用户登陆状态
        logout(request)

        # 跳转到登陆
        return redirect(reverse('user:login'))



# /user/
class UserInfoView(LoginRequiredMixin, View):
    '''用户中心-信息页面'''
    def get(self, request):
        '''显示'''

        # 获取登录用户
        user = request.user

        # 获取用户的默认收货地址
        # from redis import StrictRedis
        # conn = StrictRedis(host='192.168.235.131', port='6379', db='4')

        address = Address.objects.get_default_address(user)

        # 返回StrictRedis类的对象
        conn = get_redis_connection('default')

        # 拼接key
        history_key = 'history_%d' % user.id

        # lrange(key, start, stop) 返回是列表
        # 获取用户最新浏览的5个商品的id
        sku_ids = conn.lrange(history_key, 0, 4)

        skus = []
        for sku_id in sku_ids:
            # 根据商品的id查询商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 追加到skus列表中
            skus.append(sku)

        # 组织模板上下文
        context = {
            'address': address,
            'skus': skus,
            'page': 'user'
        }


        return render(request, 'user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    '''用户订单页面'''
    def get(self, request):

        return render(request, 'user_center_order.html', {'page':'order'})


# /user/site
class UserSiteView(LoginRequiredMixin, View):
    '''用户收货地址也页面'''
    def get(self, request):
        '''显示'''
        # 获取登录用户
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None

        address = Address.objects.get_default_address(user)

        # 组织模板
        context = {
            'page': 'address',
            'address': address,
        }
        # 使用模板

        return render(request,'user_center_site.html', context)

    def post(self, request):
        '''地址添加'''
        # 接收参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 参数校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg':'信息不完整'})

        # 校验手机号
        # 业务处理：添加收货地址

        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None

        address = Address.objects.get_default_address(user)

        is_default = True
        if address is not None:
            is_default = False
        # 如果用户已经有默认地址，新添加的地址作为非默认地址，否则为默认地址

        Address.objects.create(
            user=user,
            receiver = receiver,
            addr = addr,
            zip_code = zip_code,
            phone = phone,
            is_default =is_default,
        )

        return redirect(reverse('user:address'))



