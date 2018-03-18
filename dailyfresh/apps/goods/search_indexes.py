from haystack import indexes
# 导入模型类
from goods.models import GoodsSKU



# 指定对于某个类的某些数据建立索引
# 索引类名：模型类名+Index
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    '''商品模型索引类'''
    # 索引字段，use_template=Ture:说明根据表的哪些字段建立索引会放在一个文件中

    text = indexes.CharField(document=True, use_template=True)


    def get_model(self):
        # 返回你的模型类

        return GoodsSKU

    # 建立索引时，是对这个方法返回的数据建立索引
    def index_queryset(self, using=None):
        return self.get_model().objects.all()