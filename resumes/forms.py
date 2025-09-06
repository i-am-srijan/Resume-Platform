from django import forms
from .models import Resume, PersonalDetails, Education, Experience, Skill, Project

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title']

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        exclude = ['resume']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['resume']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ['resume']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ['resume']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['resume']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

EducationFormSet = forms.inlineformset_factory(
    Resume, Education, form=EducationForm, extra=1, can_delete=True
)

ExperienceFormSet = forms.inlineformset_factory(
    Resume, Experience, form=ExperienceForm, extra=1, can_delete=True
)

SkillFormSet = forms.inlineformset_factory(
    Resume, Skill, form=SkillForm, extra=1, can_delete=True
)

ProjectFormSet = forms.inlineformset_factory(
    Resume, Project, form=ProjectForm, extra=1, can_delete=True
)