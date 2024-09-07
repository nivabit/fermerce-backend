from esmerald import Gateway

from fermerce.app.market.category.api.v1 import ProductCategoryAPIView


route_patterns = [Gateway("/", handler=ProductCategoryAPIView)]
