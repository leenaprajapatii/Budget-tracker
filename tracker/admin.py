from django.contrib import admin
from .models import Transaction, Category, Goal

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'date', 'is_income')
    list_filter = ('user', 'is_income', 'date')
    search_fields = ('user__username', 'category__name', 'description')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_income')
    list_filter = ('is_income', 'user')
    search_fields = ('name', 'user__username')

class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'progress_percentage', 'deadline', 'completed')
    list_filter = ('user', 'completed')
    search_fields = ('name', 'user__username')
    
    def progress_percentage(self, obj):
        return f"{obj.progress():.0f}%"
    progress_percentage.short_description = 'Progress'

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Goal, GoalAdmin)