from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Data Modeli
class Data(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Veri"
        verbose_name_plural = "Veriler"

# Sorumlu Kişi Modeli
class ResponsiblePerson(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='responsible_person'
    )
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sorumlu Kişi"
        verbose_name_plural = "Sorumlu Kişiler"
        ordering = ['name']

# Hammadde Modeli
class RawMaterial(models.Model):
    entry_date = models.DateField(verbose_name="Giriş Tarihi")
    stock_code = models.CharField(max_length=100, verbose_name="Stok Kodu")
    material_name = models.CharField(max_length=200, verbose_name="Malzeme Adı")
    inc = models.CharField(max_length=100, verbose_name="INC")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        ordering = ['-entry_date']
        verbose_name = "Hammadde"
        verbose_name_plural = "Hammaddeler"

    def __str__(self):
        return f"{self.material_name} - {self.stock_code}"

# Ürün Tipi Modeli
class ProductType(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Ürün Kodu")
    name = models.CharField(max_length=100, verbose_name="Ürün Adı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        ordering = ['code']
        verbose_name = "Ürün Tipi"
        verbose_name_plural = "Ürün Tipleri"

    def __str__(self):
        return f"{self.code} - {self.name}"

# Proje Modeli
class Project(models.Model):
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    project_no = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=255, verbose_name="Proje Adı")
    recipe_code = models.CharField(max_length=50, verbose_name="Reçete Kodu")
    recipe_name = models.CharField(max_length=255, verbose_name="Reçete Adı")
    responsible_person = models.ForeignKey(
        ResponsiblePerson, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sorumlu Kişi"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"

    def __str__(self):
        return f"{self.project_no} - {self.project_name}"

# Arşivli Projeler Modeli
class ArchivedProject(models.Model):
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    project_no = models.CharField(max_length=50, verbose_name="Proje No")
    project_name = models.CharField(max_length=255, verbose_name="Proje Adı")
    recipe_code = models.CharField(max_length=50, verbose_name="Reçete Kodu")
    recipe_name = models.CharField(max_length=255, verbose_name="Reçete Adı")
    responsible_person = models.ForeignKey(
        ResponsiblePerson, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sorumlu Kişi"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Notlar")
    archived_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Arşivlenme Tarihi")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Arşivlenmiş Proje"
        verbose_name_plural = "Arşivlenmiş Projeler"

    def __str__(self):
        return f"{self.project_no} - {self.project_name}"

# Reçete Modeli
class Recipe(models.Model):
    date = models.DateField(verbose_name="Tarih")
    recipe_code = models.CharField(max_length=100, verbose_name="Reçete Kodu")
    recipe_name = models.CharField(max_length=200, verbose_name="Reçete Adı")
    project_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="Proje No")
    project_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Proje Adı")
    responsible_person = models.ForeignKey(
        ResponsiblePerson, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Sorumlu Kişi"
    )
    product_type = models.ForeignKey(
        ProductType, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Ürün Tipi"
    )
    result = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sonuç")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        ordering = ['-date']
        verbose_name = "Reçete"
        verbose_name_plural = "Reçeteler"

    def __str__(self):
        return f"{self.recipe_code} - {self.recipe_name}"

# Reçete Hammadde İlişki Modeli
class RecipeMaterial(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='materials', verbose_name="Reçete")
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, verbose_name="Hammadde")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        unique_together = ('recipe', 'material')
        verbose_name = "Reçete Hammaddesi"
        verbose_name_plural = "Reçete Hammaddeleri"

    def __str__(self):
        return f"{self.recipe.recipe_code} - {self.material.material_name}"