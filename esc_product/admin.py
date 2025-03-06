from django.contrib import admin
from .models import Product, ProductImage, Certification, Materials, MainCategory, RootCategory

# Register your models here.

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Certification)
admin.site.register(Materials)