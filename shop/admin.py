from django.contrib import admin
from .models import Product, Profile, Order, CartItem, Store

admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Store)
