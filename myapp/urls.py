from django.urls import path
from . import views

urlpatterns = [
    # Authentication & Core Pages
    path('', views.login_view, name='login'),  # Ana sayfa login
    path('home/', views.home, name='home'),    # Dashboard/Ana sayfa
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Responsible People Management
    path('responsible-people/', views.responsible_people_view, name='responsible_people'),
    path('responsible-people/delete/<int:person_id>/', views.delete_person, name='delete_person'),
    
    # Raw Materials Management
    path('raw-materials/', views.raw_materials_view, name='raw_materials'),
    path('raw-materials/delete/<int:material_id>/', views.delete_raw_material, name='delete_raw_material'),
    path('raw-materials/api/list/', views.raw_materials_api_list, name='raw_materials_api_list'),
    
    # Product Types Management
    path('product-types/', views.product_types_view, name='product_types'),
    path('product-types/edit/<int:product_id>/', views.edit_product_type, name='edit_product_type'),
    path('product-types/delete/<int:type_id>/', views.delete_product_type, name='delete_product_type'),
    
    # Projects Management
    path('projects/', views.projects_view, name='projects'),
    path('projects/add/', views.add_project_view, name='add_project'),
    path('projects/edit/<int:project_id>/', views.edit_project_view, name='edit_project'),
    path('projects/archive/<int:project_id>/', views.archive_project_view, name='archive_project'),
    path('projects/unarchive/<int:project_id>/', views.unarchive_project_view, name='unarchive_project'),

    # Recipes Management
    path('recipes/', views.recipes_view, name='recipes'),
    path('recipes/create/', views.create_recipe_view, name='create_recipe'),
    path('recipes/delete/<int:recipe_id>/', views.delete_recipe_view, name='delete_recipe'),
    path('recipes/get/<int:recipe_id>/', views.get_recipe_view, name='get_recipe'),
    path('recipes/edit/<int:recipe_id>/', views.edit_recipe_view, name='edit_recipe'),

    # Archive Management
    path('archive/', views.archive_view, name='archive'),
    path('archive/delete/<int:project_id>/', views.delete_archived_project, name='delete_archived_project'),
]
