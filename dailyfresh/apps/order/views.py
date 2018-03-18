from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from goods.models import GoodsSKU
from user.models import Address
from order.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection
# Create your views here.

# 提交订单页面视图
# /order/place

class OrderPlaceView(View):
    '''提交订单页面'''
    def post(self, request):
        #获取登录用户
        user = request.user
        # print(user)
        # QueryDict getlist
        #获取用户所要购买的商品的id
        # sku_ids通过前端的form表单提交到后端
        sku_ids = request.POST.getlist('sku_ids')

        #获取用户收货地址的信息
        addrs = Address.objects.filter(user=user)
        #print(addrs)
        #获取redis链接
        conn = get_redis_connection('default')

        #拼接key
        cart_key = 'cart_%d' % user.id

        # 遍历sku_ids获取用户所要购买的商品的信息
        skus = []
        total_count = 0
        total_amount = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            count = conn.hget(cart_key, sku_id)
            amount = int(count)*sku.price

            sku.count = count
            sku.amount = amount

            skus.append(sku)
            total_count += int(count)
            total_amount += amount

        transit_price = 10
        # 实付款
        total_pay = total_amount + transit_price

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'addrs': addrs,
            'total_pay': total_pay,
            'transit_price': transit_price,
            'sku_ids':','.join(sku_ids)
        }

        return render(request, 'place_order.html', context)


# 订单创建
# 采用ajax post请求
# /order/commit
# 前端传递的参数：收货地址id(addr_id) 支付方式(pay_method) 用户所要购买的全部商品的id(sku_ids)
#

'''
   订单创建的流程
    1) 接收参数
    2) 参数校验
    3) 组织订单信息
    4) todo: 向df_order_info中添加一条记录
    5) todo： 订单中包含几个商品需要df_order_goods中添加几条记录
        5.1 将sku_ids分割成一个列表
        5.2 遍历sku_ids，向df_order_goos中添加记录
            5.2.1 根据id获取商品的信息
            5.2.2 从redis中获取用户购买的商品的数量
            5.2.3 向df_order_goods中添加一条记录
            5.2.4 减少商品库存，增加销量
            5.2.5 累加计算订单中商品的总数目和总价格
    6) 更新订单信息中商品的总数目和总价格
    7) 删除购物车中对应的记录
'''


# 订单事物
class OrderCommitView(View):
    '''订单创建'''
    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        # print(addr_id+'---'+pay_method+'---'+sku_ids)
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        print(1)
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})
        print(2)
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 3, 'errmsg': '非法的支付方式'})
        print(3)
        # 组织订单信息
        # 组织订单id: 20180316115930+用户id
        from datetime import datetime
        order_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(user.id)

        transit_price = 10
        total_count = 0
        total_price = 0
        print(3.1)
        # todo: 向df_order_info中添加一条记录
        order = OrderInfo.objects.create(
            order_id = order_id,
            user = user,
            addr = addr,
            pay_method = pay_method,
            total_count = total_count,
            total_price = total_price,
            transit_price = transit_price,
        )
        print(4)
        # todo: 订单中包含几个商品需要向df_order_goods中添加几条记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})
            count = conn.hget(cart_key, sku_id)

            OrderGoods.objects.create(
                order = order,
                sku = sku,
                count = count,
                price = sku.price,
            )
            print(5)
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()
            print(6)
            # 累加计算订单中商品的总数目和总价格
            total_count += int(count)
            total_price += sku.price * int(count)
        print(7)
        # todo: 更新订单信息中商品的总数目和总价格
        order.total_count += total_count
        order.total_price += total_price
        order.save()
        print(8)
        # todo: 删除购物车中对应的记录
        # hdel(key, *args)
        conn.hdel(cart_key, *sku_ids)

        return JsonResponse({'res': 5, 'errmsg': '订单创建成功'})








