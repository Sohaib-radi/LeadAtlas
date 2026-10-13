from django.contrib import admin

from .models import Business, Search


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("city", "country", "sector", "keyword", "result_count", "created_at")
    list_filter = ("sector", "country")
    search_fields = ("city", "country", "keyword")


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "city", "country", "phone", "website", "status")
    list_filter = ("status", "sector", "country", "city")
    search_fields = ("name", "address", "phone", "email", "website")
    list_editable = ("status",)
    readonly_fields = ("external_id", "source", "created_at", "updated_at")
