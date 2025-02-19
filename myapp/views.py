from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import (
    Data, 
    ArchivedProject, 
    Project, 
    ResponsiblePerson, 
    RawMaterial, 
    ProductType, 
    Recipe,
    RecipeMaterial
)

# Helper Functions
def is_admin(user):
    return user.is_superuser

def generate_next_project_no():
    last_project = Project.objects.all().order_by('-project_no').first()
    last_archived_project = ArchivedProject.objects.all().order_by('-project_no').first()
    
    if last_project and last_archived_project:
        try:
            last_no = max(int(last_project.project_no), int(last_archived_project.project_no))
            next_no = str(last_no + 1).zfill(2)
        except ValueError:
            next_no = "01"
    elif last_project:
        try:
            last_no = int(last_project.project_no)
            next_no = str(last_no + 1).zfill(2)
        except ValueError:
            next_no = "01"
    elif last_archived_project:
        try:
            last_no = int(last_archived_project.project_no)
            next_no = str(last_no + 1).zfill(2)
        except ValueError:
            next_no = "01"
    else:
        next_no = "01"
    
    return next_no

def raw_materials_api_list(request):
    materials = RawMaterial.objects.all().values('id', 'stock_code', 'material_name', 'inc')
    return JsonResponse(list(materials), safe=False)

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            messages.success(request, f'Hoş geldiniz, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre!')
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')

# Basic Page Views
def home(request):
    try:
        records = Data.objects.all()
        return render(request, 'index.html', {
            'records': records, 
            'username': request.session.get('username')
        })
    except Exception as e:
        messages.error(request, f'Hata: {str(e)}')
        return redirect('home')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# Responsible People Views
@login_required
@user_passes_test(is_admin)
def responsible_people_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

            if not all([name, username, password]):
                messages.error(request, 'Tüm alanları doldurunuz.')
                return redirect('responsible_people')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Bu kullanıcı adı zaten kullanılmakta!')
                return redirect('responsible_people')

            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=False,
                    is_superuser=False
                )

                ResponsiblePerson.objects.create(
                    name=name,
                    user=user
                )

                messages.success(request, f'{name} başarıyla eklendi.')

        except Exception as e:
            messages.error(request, f'Bir hata oluştu: {str(e)}')
            if transaction.get_connection().in_atomic_block:
                transaction.set_rollback(True)

        return redirect('responsible_people')

    people = ResponsiblePerson.objects.select_related('user').all()
    return render(request, 'responsible_people.html', {'people': people})

@login_required
@user_passes_test(is_admin)
def delete_person(request, person_id):
    if request.method == 'POST':
        try:
            person = ResponsiblePerson.objects.get(id=person_id)
            user = person.user
            person_name = person.name

            with transaction.atomic():
                person.delete()
                if user and not user.is_superuser:
                    user.delete()
            
            messages.success(request, f'{person_name} başarıyla silindi.')
            
        except ResponsiblePerson.DoesNotExist:
            messages.error(request, 'Silinmek istenen kişi bulunamadı.')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
    else:
        messages.error(request, 'Geçersiz istek yöntemi.')
    
    return redirect('responsible_people')

# Raw Materials Views
@login_required
def raw_materials_view(request):
    if request.method == 'POST':
        try:
            RawMaterial.objects.create(
                entry_date=request.POST.get('entry_date'),
                stock_code=request.POST.get('stock_code'),
                material_name=request.POST.get('material_name'),
                inc=request.POST.get('inc'),
                quantity=request.POST.get('quantity')
            )
            
            messages.success(request, 'Hammadde başarıyla eklendi.')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
        return redirect('raw_materials')
    
    materials = RawMaterial.objects.all().order_by('-entry_date')
    return render(request, 'raw_materials.html', {'materials': materials})

@login_required
def delete_raw_material(request, material_id):
    if request.method == 'POST':
        try:
            material = RawMaterial.objects.get(id=material_id)
            material.delete()
            messages.success(request, 'Hammadde başarıyla silindi.')
        except RawMaterial.DoesNotExist:
            messages.error(request, 'Silinmek istenen hammadde bulunamadı.')
        except Exception as e:
            messages.error(request, f'Hata: {str(e)}')
    return redirect('raw_materials')

# Product Types Views
@login_required
def product_types_view(request):
    if request.method == 'POST':
        try:
            code = request.POST.get('code')
            name = request.POST.get('name')
            
            if code and name:
                if ProductType.objects.filter(code=code).exists():
                    messages.error(request, 'Bu kod zaten kullanılmakta.')
                else:
                    ProductType.objects.create(code=code, name=name)
                    messages.success(request, 'Ürün tipi başarıyla eklendi.')
            else:
                messages.error(request, 'Kod ve isim alanları zorunludur.')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
        return redirect('product_types')
    
    product_types = ProductType.objects.all().order_by('code')
    return render(request, 'product_types.html', {'product_types': product_types})

@login_required
def edit_product_type(request, product_id):
    product_type = get_object_or_404(ProductType, id=product_id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        
        if code and name:
            if code != product_type.code and ProductType.objects.filter(code=code).exists():
                messages.error(request, 'Bu kod zaten kullanılmakta.')
                return render(request, 'edit_product_type.html', {'product': product_type})
            
            product_type.code = code
            product_type.name = name
            product_type.save()
            messages.success(request, 'Ürün tipi başarıyla güncellendi.')
            return redirect('product_types')
        else:
            messages.error(request, 'Kod ve isim alanları zorunludur.')
    
    return render(request, 'edit_product_type.html', {'product': product_type})

@login_required
def delete_product_type(request, type_id):
    if request.method == 'POST':
        try:
            product_type = get_object_or_404(ProductType, id=type_id)
            product_type.delete()
            messages.success(request, 'Ürün tipi başarıyla silindi.')
        except Exception as e:
            messages.error(request, f'Hata: {str(e)}')
    else:
        messages.error(request, 'Geçersiz istek yöntemi.')
    return redirect('product_types')

# Projects Views
@login_required
def projects_view(request):
    try:
        # Admin tüm projeleri görebilir
        if request.user.is_superuser:
            projects = Project.objects.all().order_by('-start_date')  # date yerine start_date kullanıldı
        else:
            # Normal kullanıcı sadece sorumlusu olduğu projeleri görebilir
            responsible_person = ResponsiblePerson.objects.get(user=request.user)
            projects = Project.objects.filter(responsible_person=responsible_person).order_by('-start_date')  # date yerine start_date kullanıldı

        context = {
            'projects': projects,
            'user': request.user,
            'is_admin': request.user.is_superuser
        }
        return render(request, 'projects.html', context)
    except ResponsiblePerson.DoesNotExist:
        messages.error(request, 'Sorumlu kişi kaydınız bulunamadı.')
        return render(request, 'projects.html', {'projects': []})
    except Exception as e:
        messages.error(request, f'Bir hata oluştu: {str(e)}')
        return render(request, 'projects.html', {'projects': []})

@login_required
@user_passes_test(is_admin)
def add_project_view(request):
    if request.method == 'POST':
        try:
            responsible_person = None
            responsible_person_id = request.POST.get('responsible_person')
            if responsible_person_id:
                responsible_person = ResponsiblePerson.objects.get(id=responsible_person_id)

            project = Project.objects.create(
                start_date=request.POST.get('start_date'),
                project_no=request.POST.get('project_no'),
                project_name=request.POST.get('project_name'),
                recipe_code=request.POST.get('recipe_code'),
                recipe_name=request.POST.get('recipe_name'),
                responsible_person=responsible_person,
                notes=request.POST.get('notes', '')
            )
            
            messages.success(request, 'Proje başarıyla oluşturuldu.')
            return redirect('projects')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
            return redirect('add_project')

    # GET isteği için form sayfasını göster
    try:
        next_project_no = generate_next_project_no()  # Helper function'ı burada çağırıyoruz
        responsible_people = ResponsiblePerson.objects.all().order_by('name')
        context = {
            'responsible_people': responsible_people,
            'next_project_no': next_project_no,
            'is_admin': request.user.is_superuser
        }
        return render(request, 'add_project.html', context)
    except Exception as e:
        messages.error(request, f'Bir hata oluştu: {str(e)}')
        return redirect('projects')

@login_required
@user_passes_test(is_admin)
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        try:
            project.start_date = request.POST.get('start_date')
            project.project_no = request.POST.get('project_no')
            project.project_name = request.POST.get('project_name')
            project.recipe_code = request.POST.get('recipe_code')
            project.recipe_name = request.POST.get('recipe_name')
            
            responsible_person_id = request.POST.get('responsible_person')
            if responsible_person_id:
                project.responsible_person = ResponsiblePerson.objects.get(id=responsible_person_id)
            else:
                project.responsible_person = None
            
            project.notes = request.POST.get('notes')
            project.save()
            
            messages.success(request, 'Proje başarıyla güncellendi.')
            return redirect('projects')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
    
    responsible_people = ResponsiblePerson.objects.all()
    return render(request, 'edit_project.html', {
        'project': project,
        'responsible_people': responsible_people
    })

@login_required
@user_passes_test(is_admin)
def archive_project_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        ArchivedProject.objects.create(
            start_date=project.start_date,
            project_no=project.project_no,
            project_name=project.project_name,
            recipe_code=project.recipe_code,
            recipe_name=project.recipe_name,
            responsible_person=project.responsible_person,
            notes=project.notes
        )
        project.delete()
        messages.success(request, f"'{project.project_name}' projesi başarıyla arşivlendi.")
    except Project.DoesNotExist:
        messages.error(request, 'Arşivlenecek proje bulunamadı.')
    except Exception as e:
        messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('projects')

@login_required
@user_passes_test(is_admin)
def unarchive_project_view(request, project_id):
    try:
        archived_project = ArchivedProject.objects.get(id=project_id)
        Project.objects.create(
            start_date=archived_project.start_date,
            project_no=archived_project.project_no,
            project_name=archived_project.project_name,
            recipe_code=archived_project.recipe_code,
            recipe_name=archived_project.recipe_name,
            responsible_person=archived_project.responsible_person,
            notes=archived_project.notes
        )
        archived_project.delete()
        messages.success(request, f"'{archived_project.project_name}' projesi başarıyla geri alındı.")
        return redirect('projects')
    except ArchivedProject.DoesNotExist:
        messages.error(request, 'Geri alınacak proje bulunamadı.')
    except Exception as e:
        messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('archive')

# Archive Views
@login_required
def archive_view(request):
    try:
        archived_projects = ArchivedProject.objects.all().order_by('-start_date')
        return render(request, 'archive.html', {'archived_projects': archived_projects})
    except Exception as e:
        messages.error(request, f"Hata oluştu: {str(e)}")
        return render(request, 'archive.html', {'archived_projects': []})

@login_required
@user_passes_test(is_admin)
def delete_archived_project(request, project_id):
    try:
        archived_project = get_object_or_404(ArchivedProject, id=project_id)
        project_name = archived_project.project_name
        archived_project.delete()
        messages.success(request, f"'{project_name}' projesi arşivden kalıcı olarak silindi.")
    except Exception as e:
        messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('archive')

# Recipe Views
@login_required
def recipes_view(request):
    try:
        # Eğer kullanıcı admin ise tüm reçeteleri göster
        if request.user.is_superuser:
            recipes = Recipe.objects.all().order_by('-date')
        else:
            # Admin değilse, önce ResponsiblePerson kaydını kontrol et
            try:
                responsible_person = ResponsiblePerson.objects.get(user=request.user)
                # Sadece kendi reçetelerini göster
                recipes = Recipe.objects.filter(responsible_person=responsible_person).order_by('-date')
            except ResponsiblePerson.DoesNotExist:
                messages.error(request, 'Sorumlu kişi kaydınız bulunamadı.')
                recipes = []

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            recipes_data = list(recipes.values())
            return JsonResponse(recipes_data, safe=False)

        context = {
            'recipes': recipes,
            'user': request.user,
            'is_admin': request.user.is_superuser
        }
        return render(request, 'recipes.html', context)

    except Exception as e:
        messages.error(request, f'Bir hata oluştu: {str(e)}')
        return render(request, 'recipes.html', {'recipes': []})

@login_required
def edit_recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Mevcut recipe bilgilerini güncelle
                recipe.date = request.POST.get('date')
                recipe.project_no = request.POST.get('project_no')
                recipe.project_name = request.POST.get('project_name')
                recipe.recipe_code = request.POST.get('recipe_code')
                recipe.recipe_name = request.POST.get('recipe_name')
                recipe.result = request.POST.get('result')
                recipe.notes = request.POST.get('notes')
                
                product_type_id = request.POST.get('product_type')
                if product_type_id:
                    recipe.product_type = ProductType.objects.get(id=product_type_id)

                recipe.save()

                # Mevcut hammaddeleri temizle
                RecipeMaterial.objects.filter(recipe=recipe).delete()

                # Yeni hammaddeleri ekle
                materials_data = []
                for key, value in request.POST.items():
                    if key.startswith('quantity_'):
                        material_id = key.split('_')[1]
                        quantity = value
                        if quantity:
                            materials_data.append(
                                RecipeMaterial(
                                    recipe=recipe,
                                    material_id=material_id,
                                    quantity=quantity
                                )
                            )
                
                RecipeMaterial.objects.bulk_create(materials_data)
                
                messages.success(request, 'Reçete başarıyla güncellendi.')
                return redirect('recipes')

        except Exception as e:
            messages.error(request, f'Hata: {str(e)}')
            return redirect('edit_recipe', recipe_id=recipe_id)

    # GET isteği için mevcut verileri yükle
    recipe_materials = RecipeMaterial.objects.filter(recipe=recipe).select_related('material')
    
    materials_json = list(recipe_materials.values(
        'material__id',
        'material__stock_code',
        'material__material_name',
        'material__inc',
        'quantity'
    ))

    # Decimal değerleri string'e çevir
    for material in materials_json:
        material['quantity'] = str(material['quantity'])

    context = {
        'recipe': recipe,
        'product_types': ProductType.objects.all().order_by('code'),
        'responsible_person': recipe.responsible_person,
        'is_admin': request.user.is_superuser,
        'recipe_materials': materials_json
    }
    return render(request, 'edit_recipe.html', context)

# Hammadde API endpoint'i için
def raw_materials_api_list(request):
    materials = RawMaterial.objects.all().values('id', 'stock_code', 'material_name', 'inc')
    return JsonResponse(list(materials), safe=False)

@login_required
def create_recipe_view(request):
    try:
        responsible_person = ResponsiblePerson.objects.get(user=request.user)
    except ResponsiblePerson.DoesNotExist:
        messages.error(request, 'Sorumlu kişi kaydınız bulunamadı.')
        return redirect('recipes')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Reçete oluşturma
                recipe = Recipe.objects.create(
                    date=request.POST.get('date'),
                    project_no=request.POST.get('project_no'),
                    project_name=request.POST.get('project_name'),
                    recipe_code=request.POST.get('recipe_code'),
                    recipe_name=request.POST.get('recipe_name'),
                    responsible_person=responsible_person,
                    product_type_id=request.POST.get('product_type'),
                    result=request.POST.get('result'),
                    notes=request.POST.get('notes')
                )

                # Hammaddeleri ekleme
                materials_data = []
                for key, value in request.POST.items():
                    if key.startswith('quantity_'):
                        material_id = key.split('_')[1]
                        quantity = value
                        if quantity:
                            materials_data.append(
                                RecipeMaterial(
                                    recipe=recipe,
                                    material_id=material_id,
                                    quantity=quantity
                                )
                            )

                RecipeMaterial.objects.bulk_create(materials_data)

                messages.success(request, 'Reçete başarıyla oluşturuldu.')
                return redirect('recipes')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
            return redirect('create_recipe')

    # GET isteği için form sayfasını göster
    projects = Project.objects.filter(responsible_person=responsible_person).order_by('project_no')
    product_types = ProductType.objects.all().order_by('code')
    return render(request, 'create_recipe.html', {
        'responsible_person': responsible_person,
        'projects': projects,
        'product_types': product_types
    })

@login_required
def delete_recipe_view(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.delete()
        messages.success(request, 'Reçete başarıyla silindi.')
    except Exception as e:
        messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('recipes')

@login_required
def get_recipe_view(request, recipe_id):
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        recipe_data = {
            'date': recipe.date.strftime('%Y-%m-%d'),
            'project_no': recipe.project_no,
            'project_name': recipe.project_name,
            'recipe_code': recipe.recipe_code,
            'recipe_name': recipe.recipe_name,
            'responsible_person': recipe.responsible_person.name,
            'product_type': recipe.product_type.id,
            'result': recipe.result,
            'notes': recipe.notes,
            'materials': list(recipe.materials.values('material_id', 'quantity'))
        }
        return JsonResponse(recipe_data)
    
    except Recipe.DoesNotExist:
        messages.error(request, 'Reçete bulunamadı.')
        return redirect('recipes')

@login_required
@user_passes_test(is_admin)
def delete_archived_project(request, project_id):
    try:
        archived_project = get_object_or_404(ArchivedProject, id=project_id)
        project_name = archived_project.project_name
        archived_project.delete()
        messages.success(request, f"'{project_name}' projesi arşivden kalıcı olarak silindi.")
    except Exception as e:
        messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('archive')