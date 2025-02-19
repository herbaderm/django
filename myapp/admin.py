from django.contrib import admin
from .models import (
    Data, ResponsiblePerson, RawMaterial, 
    ProductType, Project, ArchivedProject, Recipe
)

@admin.register(ResponsiblePerson)
class ResponsiblePersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at', 'updated_at')

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_name', 'stock_code', 'entry_date', 'quantity')
    search_fields = ('material_name', 'stock_code')
    list_filter = ('entry_date',)

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_no', 'start_date', 'responsible_person')
    search_fields = ('project_name', 'project_no', 'recipe_name')
    list_filter = ('start_date', 'responsible_person')

@admin.register(ArchivedProject)
class ArchivedProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_no', 'start_date', 'responsible_person')
    search_fields = ('project_name', 'project_no', 'recipe_name')
    list_filter = ('start_date', 'responsible_person')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe_name', 'recipe_code', 'project_name', 'responsible_person')
    search_fields = ('recipe_name', 'recipe_code', 'project_name')
    list_filter = ('date', 'responsible_person')

@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'content')