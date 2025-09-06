from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from io import BytesIO
from xhtml2pdf import pisa
from .models import Resume, PersonalDetails, Education, Experience, Skill, Project
from .forms import (
    ResumeForm, PersonalDetailsForm, EducationFormSet, 
    ExperienceFormSet, SkillFormSet, ProjectFormSet
)

@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})

@login_required
def resume_create(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            
            # If this is the first resume, set it as default
            if not Resume.objects.filter(user=request.user).exists():
                resume.is_default = True
                
            resume.save()
            
            # Create empty personal details
            PersonalDetails.objects.create(resume=resume)
            
            messages.success(request, 'Resume created successfully! You can now add your details.')
            return redirect('resumes:resume_edit', resume_id=resume.id)
    else:
        form = ResumeForm()
    
    return render(request, 'resumes/resume_create.html', {'form': form})

@login_required
def resume_edit(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    create_new_version = False
    
    if request.method == 'POST':
        # Check if we should create a new version
        if 'save_as_new' in request.POST:
            create_new_version = True
        
        personal_details_form = PersonalDetailsForm(request.POST, instance=resume.personal_details)
        education_formset = EducationFormSet(request.POST, instance=resume, prefix='education')
        experience_formset = ExperienceFormSet(request.POST, instance=resume, prefix='experience')
        skill_formset = SkillFormSet(request.POST, instance=resume, prefix='skills')
        project_formset = ProjectFormSet(request.POST, instance=resume, prefix='projects')
        
        if (personal_details_form.is_valid() and education_formset.is_valid() and 
            experience_formset.is_valid() and skill_formset.is_valid() and project_formset.is_valid()):
            
            if create_new_version:
                # Create a new version
                new_resume = Resume.objects.create(
                    user=request.user,
                    title=resume.title + " (Copy)",
                    version=resume.version + 1,
                    previous_version=resume,
                    is_default=resume.is_default
                )
                
                # Copy personal details
                personal_details = personal_details_form.save(commit=False)
                personal_details.resume = new_resume
                personal_details.pk = None
                personal_details.save()
                
                # Copy education
                for form in education_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        edu = form.save(commit=False)
                        edu.resume = new_resume
                        edu.pk = None
                        edu.save()
                
                # Copy experience
                for form in experience_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        exp = form.save(commit=False)
                        exp.resume = new_resume
                        exp.pk = None
                        exp.save()
                
                # Copy skills
                for form in skill_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        skill = form.save(commit=False)
                        skill.resume = new_resume
                        skill.pk = None
                        skill.save()
                
                # Copy projects
                for form in project_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        project = form.save(commit=False)
                        project.resume = new_resume
                        project.pk = None
                        project.save()
                
                messages.success(request, 'New version created successfully!')
                return redirect('resumes:resume_edit', resume_id=new_resume.id)
            else:
                # Save changes to current resume
                personal_details_form.save()
                education_formset.save()
                experience_formset.save()
                skill_formset.save()
                project_formset.save()
                
                messages.success(request, 'Resume updated successfully!')
                return redirect('resumes:resume_detail', resume_id=resume.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        personal_details_form = PersonalDetailsForm(instance=resume.personal_details)
        education_formset = EducationFormSet(instance=resume, prefix='education')
        experience_formset = ExperienceFormSet(instance=resume, prefix='experience')
        skill_formset = SkillFormSet(instance=resume, prefix='skills')
        project_formset = ProjectFormSet(instance=resume, prefix='projects')
    
    context = {
        'resume': resume,
        'personal_details_form': personal_details_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
        'skill_formset': skill_formset,
        'project_formset': project_formset,
    }
    
    return render(request, 'resumes/resume_edit.html', context)

@login_required
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return render(request, 'resumes/resume_detail.html', {'resume': resume})

@login_required
def resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    try:
        # Render HTML template
        html_string = render_to_string('resumes/resume_pdf.html', {'resume': resume})
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(html_string, dest=buffer)
        
        # If PDF generation failed
        if pisa_status.err:
            messages.error(request, 'PDF generation failed. Please try again.')
            return redirect('resumes:resume_detail', resume_id=resume.id)
        
        # Get PDF value from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create HTTP response with PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
        response.write(pdf)
        
        return response
    except Exception as e:
        messages.error(request, f'PDF generation error: {str(e)}')
        return redirect('resumes:resume_detail', resume_id=resume.id)

@login_required
def resume_delete(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        title = resume.title
        resume.delete()
        messages.success(request, f'Resume "{title}" has been deleted successfully.')
        return redirect('resumes:resume_list')
    
    return render(request, 'resumes/resume_delete.html', {'resume': resume})