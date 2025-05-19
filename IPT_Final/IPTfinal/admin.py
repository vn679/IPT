from django.contrib import admin
from .models import SalesData, ProjectStatus, TodoItem, RevenueMetrics, VisitorMetrics

@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'product_category', 'amount')
    list_filter = ('date', 'product_category')
    search_fields = ('product_category',)

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'progress', 'deadline', 'created_at')
    list_filter = ('status', 'deadline')
    search_fields = ('name',)

@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'completed', 'created_at')
    list_filter = ('completed', 'created_at', 'user')
    search_fields = ('title', 'user__username')

@admin.register(RevenueMetrics)
class RevenueMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'expenses', 'net_profit')
    list_filter = ('date',)

@admin.register(VisitorMetrics)
class VisitorMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'page_views', 'unique_visitors', 'bounce_rate')
    list_filter = ('date',) 