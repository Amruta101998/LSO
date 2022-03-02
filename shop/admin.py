from django.contrib import admin

# Register your models here.
from .models import *
# from django.contrib.auth.models import
from django.contrib.auth.admin import UserAdmin
from .models import Review


class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'update_desc', 'timestamp')
    list_filter = ['timestamp']

    def has_delete_permission(self, request, obj=None):
        return False


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'userId', 'name', 'email', 'timestamp')
    list_filter = ['timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','product', 'rate', 'created_at']
    readonly_fields = ['created_at',]

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price')
    list_filter = ['category']
    search_fields = ['product_name']


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'email', 'timestamp')
    list_filter = ['timestamp']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False



admin.site.register(Product, ProductAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderUpdate, OrderUpdateAdmin)
admin.site.register(Profile)
admin.site.register(Review, ReviewAdmin)

admin.site.site_header = "Let Serve Others"
admin.site.index_title = "Let Serve Others Administration"
admin.site.site_title = "Let Serve Others Admin"

