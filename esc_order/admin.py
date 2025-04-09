from django.contrib import admin
from .models import SwapOrder, ShippingDetails, Address


# Register your models here.

admin.site.register(SwapOrder)
admin.site.register(ShippingDetails)
admin.site.register(Address)
