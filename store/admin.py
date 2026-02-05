from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product, SiteSetting, Order, OrderItem, GalleryItem, Review, ContactMessage


class CategoryAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug"]
    search_fields = ["name"]


class ProductAdmin(ModelAdmin):
    list_display = ["name", "category", "price", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


class SiteSettingAdmin(ModelAdmin):
    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return super().has_add_permission(request)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "qty", "unit_price", "line_total"]


class OrderAdmin(ModelAdmin):
    list_display = ["reference", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["reference", "full_name", "email", "phone"]
    readonly_fields = [
        "reference",
        "subtotal",
        "delivery_fee",
        "total",
        "status",
        "created_at",
        "paynow_reference",
        "paynow_poll_url",
        "paynow_redirect_url",
    ]
    inlines = [OrderItemInline]


class GalleryItemForm(forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ["image", "video", "caption"]

    def clean(self):
        data = super().clean()
        image, video = data.get("image"), data.get("video")
        if not image and not video:
            raise forms.ValidationError("Add either an image or a video.")
        if image and video:
            raise forms.ValidationError("Add only an image or a video, not both.")
        return data


class GalleryItemAdmin(ModelAdmin):
    form = GalleryItemForm
    list_display = ["__str__", "created_at", "has_image", "has_video"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True

    def has_video(self, obj):
        return bool(obj.video)

    has_video.boolean = True


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(GalleryItem, GalleryItemAdmin)


class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "email", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "phone", "message", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ContactMessage, ContactMessageAdmin)


class ReviewAdmin(ModelAdmin):
    list_display = ["name", "rating", "created_at", "is_visible"]
    list_filter = ["is_visible", "rating", "created_at"]
    search_fields = ["name", "text"]
    list_editable = ["is_visible"]


admin.site.register(Review, ReviewAdmin)

