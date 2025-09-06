from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from resumes.models import Resume

@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    default_resume = resumes.filter(is_default=True).first()
    
    context = {
        'resumes': resumes,
        'default_resume': default_resume,
        'resume_count': resumes.count(),
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def resume_versions(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get all versions of this resume
    versions = []
    current = resume
    
    # Traverse backwards through versions
    while current:
        versions.append(current)
        current = current.previous_version
    
    # Sort by version number (descending)
    versions.sort(key=lambda x: x.version, reverse=True)
    
    context = {
        'resume': resume,
        'versions': versions,
    }
    
    return render(request, 'dashboard/resume_versions.html', context)