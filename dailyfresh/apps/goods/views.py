from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.generic import View
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from order.models import OrderGoods
# Create your views here


class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示'''
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')

        # 判断缓存中是否有没有数据
        if context is None:


            # 获取商品的分类信息
            types = GoodsType.objects.all()

            # 获取首页的轮播商品的信息
            index_banner = IndexGoodsBanner.objects.all().order_by('index')

            # 获取首页的促销活动的信息
            promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品的展示信息
            for type in types:
                # 获取type种类在首页展示的信息
                image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
                title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)

                # 给type对象增加属性title_banner,image_banner
                type.title_banner = title_banner
                type.image_banner = image_banner
                print(type.title_banner)
            context = {
                'types': types,
                'index_banner': index_banner,
                'promotion_banner': promotion_banner,
                'cart_count': 0,
            }
            # 设置首页缓存
            # from django.core.cache import cache
            # cache.set('缓存名称', '缓存数据', '缓存有效时间'} pickle
            # 缓存时间最好是设计一下，前端更新数据时，1小时后也可以清楚掉
            cache.set('index_page_data', context, 3600)




        # 判断用户是否已经登录
        cart_count = 0
        if request.user.is_authenticated():
            # 获取redis连接
            conn = get_redis_connection('default')
            # 拼接key
            cart_key = 'cart_%s' % request.user.id
            # 获取用户购物车中商品的条目数
            # hlen(key)->返回属性的数目
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文，更新数据里面的cart_count数据信息
        context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)




# 详情页视图
# 前端传递的参数: 商品id(sku_id)
# 前端传递的参数的方式:
# 1) url捕获  /goods/商品id
# 2) get传递  /goods?sku_id=商品id
# 3) post传递


# /goods/商品id
class DetailView(View):
    '''详情页视图'''
    def get(self, request, sku_id):
        # 获取商品的详情信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取商品分类的信息
        types = GoodsType.objects.all()

        # 获取用户评论
        order_skus = OrderGoods.objects.filter(sku=sku).exclude(comment='').order_by('-update_time')

        # 获取和商品同一个SPU的其他规格的商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)

        # 获取和商品同一种类的两个新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).exclude(id=sku_id).order_by('-create_time')[:2]

        # 判断用户是否已经登录
        cart_count = 0
        if request.user.is_authenticated():
            # 获取redis连接
            conn = get_redis_connection('default')
            # 拼接key
            cart_key = 'cart_%s' % request.user.id
            # 获取用户购物车中商品的条目数
            # hlen(key)->返回属性的数目
            cart_count = conn.hlen(cart_key)

            # 添加历史浏览记录
            conn = get_redis_connection('default')

            history_key = 'history_%d' % request.user.id
            # 先尝试移除列表中sku_id
            conn.lrem(history_key, 0, sku_id)
            # 将sku_id插入到列表的左侧
            conn.lpush(history_key, sku_id)
            # 只保留用户浏览的最新5个商品
            conn.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'types':  types,
            'order_skus': order_skus,
            'same_spu_skus': same_spu_skus,
            'new_skus': new_skus,
            'cart_count': cart_count,

        }
        return render(request, 'detail.html', context)


# 列表页视图
# flask restful api
# 前端传递的参数: 种类id(type_id) 页码(page) 排序方式(sort)
# /list?type_id=种类id&page=页码&sort=排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码?sort=排序方式  采用这种

class ListView(View):
    '''列表页'''
    def get(self, request, type_id, page):
        '''显示'''
        # 获取参数
        # 获取type_id对应的商品种类的信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取所有商品种类的信息
        types = GoodsType.objects.all()

        # 获取排序方式
        # sort=price: 按照商品的价格(price)从低到高排序
        # sort=hot: 按照商品的人气(sales)从高到低排序
        # sort=default: 按照默认排序方式(id)从高到低排序
        sort = request.GET.get('sort')


        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 分页操作
        from django.core.paginator import Paginator
        paginator = Paginator(skus, 1)

        page = int(page)

        if page > paginator.num_pages:
            page = 1

        # 获取第page页内容, 返回Page类的实例对象
        skus_page = paginator.page(page)

        # 页码处理
        # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
        # 1) 分页页码小于5页，显示全部页码
        # 2）当前页属于1-3页，显示1-5页
        # 3) 当前页属于后3页，显示后5页
        # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages+1)
        elif page <=3:
            pages = range(1,6)
        elif num_pages - page <= 2:
            pages = range(num_pages-2, num_pages+1)
        else:
            pages = range(num_pages-2, num_pages+3)

        # 获取和商品同一种类的两个新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        cart_count = 0
        if request.user.is_authenticated():

            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % request.user.id
            cart_count = conn.hlen(cart_key)

        context = {
            'type': type,
            'types': types,
            'sort': sort,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'skus_page': skus_page,
            'pages': pages
        }

        return render(request, 'list.html', context)