from django import forms
from .models import Project, ResponsiblePerson

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['start_date', 'project_no', 'project_name', 'recipe_code', 'recipe_name', 'responsible_person', 'notes']

    responsible_person = forms.ModelChoiceField(
        queryset=ResponsiblePerson.objects.all(),
        empty_label="Bir kişi seçin",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
