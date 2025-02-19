from django.urls import path
from . import views

urlpatterns = [
    # Ana sayfalar
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Kullanıcı işlemleri
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Sorumlu kişiler
    path('responsible_people/', views.responsible_people_view, name='responsible_people'),
    path('delete_person/<int:person_id>/', views.delete_person, name='delete_person'),
    
    # Hammaddeler
    path('raw_materials/', views.raw_materials_view, name='raw_materials'),
    path('delete_raw_material/<int:material_id>/', views.delete_raw_material, name='delete_raw_material'),
    path('raw_materials/api/list/', views.raw_materials_api_list, name='raw_materials_api_list'),
    
    # Ürün tipleri
    path('product_types/', views.product_types_view, name='product_types'),
    path('edit_product_type/<int:product_id>/', views.edit_product_type, name='edit_product_type'),
    path('delete_product_type/<int:type_id>/', views.delete_product_type, name='delete_product_type'),
    
    # Projeler
    path('projects/', views.projects_view, name='projects'),
    path('add_project/', views.add_project_view, name='add_project'),
    path('edit_project/<int:project_id>/', views.edit_project_view, name='edit_project'),
    path('archive_project/<int:project_id>/', views.archive_project_view, name='archive_project'),
    path('unarchive_project/<int:project_id>/', views.unarchive_project_view, name='unarchive_project'),

    # Reçeteler
    path('recipes/', views.recipes_view, name='recipes'),
    path('create_recipe/', views.create_recipe_view, name='create_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe_view, name='delete_recipe'),
    path('get_recipe/<int:recipe_id>/', views.get_recipe_view, name='get_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.edit_recipe_view, name='edit_recipe'),

    # Arşiv
    path('archive/', views.archive_view, name='archive'),
    path('delete_archived_project/<int:project_id>/', views.delete_archived_project, name='delete_archived_project'),
]