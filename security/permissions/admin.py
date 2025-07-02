from django.contrib import admin
from .models import Module, Permission, GroupModulePermission


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('order', 'name')
    list_editable = ('is_active', 'order')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'module', 'description', 'is_active')
    list_filter = ('module', 'is_active')
    search_fields = ('name', 'codename', 'description')
    ordering = ('module', 'name')
    list_editable = ('is_active',)


@admin.register(GroupModulePermission)
class GroupModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'permission', 'is_active', 'updated_at')
    list_filter = ('group', 'permission__module', 'is_active')
    search_fields = ('group__name', 'permission__name')
    date_hierarchy = 'updated_at'
    list_editable = ('is_active',)
