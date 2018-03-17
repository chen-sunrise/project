from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新时调用'''
        # 调用ModelAdmin中save_model来实现更新或新增
        super().save_model(request, obj, form, change)

        # 附加操作：发生生成静态首页的任务
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 附加操作：清除首页缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除数据时调用'''
        # 调用ModelAdmin中delete_model来实现删除操作
        super().delete_model(request, obj)

        # 附加操作：发生生成静态首页的任务
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 附加操作：清除首页缓存
        cache.delete('index_page_data')

class GoodeTypeAdmin(BaseModelAdmin):
    '''商品种类模型admin管理类'''
    pass

class IndexGoodsBannerAdmin(BaseModelAdmin):
    '''首页轮播商品模型admin管理类'''
    pass

class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    '''首页分类商品展示信息admin管理类'''
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    '''首页促销活动商品模型admin管理类'''
    pass


admin.site.register(GoodsType,GoodeTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)