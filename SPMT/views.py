from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from StudentProjectManagementTool import settings
from .forms import ProfessorLoginForm, StudentLoginForm, StudentSignupForm, ProjectSubmissionForm
from .models import CustomUser,Student,ProjectSubmission
from django.http import JsonResponse
import logging
logger = logging.getLogger(__name__)

def home(request):
    # Initialize forms
    professor_login_form = ProfessorLoginForm()
    student_login_form = StudentLoginForm()
    student_signup_form = StudentSignupForm()

    if request.method == 'POST':
        if 'professor_login' in request.POST:
            form = ProfessorLoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_professor:
                    login(request, user)
                    return redirect('professor_dashboard')
                else:
                    messages.error(request, 'Invalid professor credentials or professor account does not exist.')

        elif 'student_login' in request.POST:
            form = StudentLoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_student:
                    login(request, user)
                    return redirect('student_dashboard')
                else:
                    return render(request, 'home.html', {'error': 'Invalid username or password'})

    else:
        # Handle GET request and determine which form to show
        show_form_value = request.GET.get('show_form', '')
        if show_form_value:
            if show_form_value == 'student-login':
                student_login_form = StudentLoginForm()
            elif show_form_value == 'student-signup':
                student_signup_form = StudentSignupForm()
            elif show_form_value == 'professor-login':
                professor_login_form = ProfessorLoginForm()

    return render(request, 'SPMT/home.html', {
        'professor_login_form': professor_login_form,
        'student_login_form': student_login_form,
        'student_signup_form': student_signup_form,
    })


def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Fetch the user with the given username
            user = CustomUser.objects.filter(username=username).first()

            if user and user.check_password(password):
                # Password is correct and user exists
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/student_dashboard/'})
            else:
                # Either user doesn't exist or password is incorrect
                return JsonResponse({'success': False, 'error': 'Invalid username or password'})
        else:
            return JsonResponse({'success': False, 'error': 'Form validation error'})
    else:
        form = StudentLoginForm()
    return render(request, 'SPMT/home.html', {'student_login_form': form})

def student_signup_view(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mob = request.POST.get('mobile_number')
        # Initialize error flag
        error_flag = False

        # Check if the username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            error_flag = True

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            error_flag = True

        # If there are errors, re-render the home page with the error messages
        if error_flag:
            messages.error(request, "Invalid details entered for registration. Please try again.")
            student_signup_form = StudentSignupForm()
            professor_login_form = ProfessorLoginForm()
            student_login_form = StudentLoginForm()

            context = {
                'student_signup_form': student_signup_form,
                'professor_login_form': professor_login_form,
                'student_login_form': student_login_form
            }

            return render(request, 'SPMT/home.html', context)

        # Save the form data manually if validations pass
        # Create and save the user manually if validations pass
        user = CustomUser(
            username=username,
            password=make_password(password1),  # Ensure password is hashed
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_type='student'
        )
        user.save()

        Student.objects.create(
            user=user,
            student_name=f"{first_name} {last_name}",
            email=email,
            mobile_number=mob,
        )

        messages.success(request, "Signup successful!")
        return render(request, 'SPMT/signup_success.html')

    else:
        form = StudentSignupForm()

    return render(request, 'SPMT/home.html', {'form': form})



def professor_login(request):
    if request.method == 'POST':
        entered_code = request.POST.get('security_code')
        if entered_code == settings.PROFESSOR_SECURITY_CODE:
            return redirect('professor_dashboard')  # Redirect to professor dashboard
        else:
            messages.error(request, 'Invalid security code. Access Terminated !')
            student_signup_form = StudentSignupForm()
            professor_login_form = ProfessorLoginForm()
            student_login_form = StudentLoginForm()

            context = {
                'student_signup_form': student_signup_form,
                'professor_login_form': professor_login_form,
                'student_login_form': student_login_form
            }

            return render(request, 'SPMT/home.html', context)

    return render(request, 'SPMT/professor_login.html')



@login_required
def student_dashboard(request):
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.save()
            return redirect('student_dashboard')
    else:
        form = ProjectSubmissionForm()

    submissions = ProjectSubmission.objects.filter(student=request.user)

    return render(request, 'SPMT/student_dashboard.html', {
        'form': form,
        'submissions': submissions,
    })


def submit_project(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        student_name = request.POST.get('student_name')
        matriculation_number = request.POST.get('matriculation_number')
        remarks = request.POST.get('remarks')
        submitted_to = request.POST.get('submitted_to')
        file = request.FILES.get('file')

        # Basic manual validation
        if not subject_name or not subject_code or not matriculation_number:
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'SPMT/student_dashboard.html', {
                'form': ProjectSubmissionForm(),git remote -v
                'submissions': ProjectSubmission.objects.filter(student=request.user),
            })git remote -v
        # Create and save the project submission manually
        project_submission = ProjectSubmission(
            subject_name=subject_name,
            subject_code=subject_code,
            student=request.user,
            student_name = student_name,
            matriculation_number=matriculation_number,
            remarks=remarks,
            submitted_to=submitted_to,
            file=file
        )
        try:
            project_submission.save()
            messages.success(request, 'Project submitted successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

        return render(request, 'SPMT/student_dashboard.html', {
            'form': ProjectSubmissionForm(),
            'submissions': ProjectSubmission.objects.filter(student=request.user),
        })
    else:
        form = ProjectSubmissionForm()
        return render(request, 'SPMT/student_dashboard.html', {
            'form': form,
            'submissions': ProjectSubmission.objects.filter(student=request.user),
        })

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!.")
    student_signup_form = StudentSignupForm()
    professor_login_form = ProfessorLoginForm()
    student_login_form = StudentLoginForm()

    context = {
        'student_signup_form': student_signup_form,
        'professor_login_form': professor_login_form,
        'student_login_form': student_login_form
    }

    return render(request, 'SPMT/home.html', context)

def professor_dashboard(request):
    submissions = ProjectSubmission.objects.all()  # Fetch all project submissions
    return render(request, 'SPMT/professor_dashboard.html', {
        'submissions': submissions,
    })


def update_grade_status(request, matriculation_number, subject_code):
    if request.method == 'POST':
        try:
            # Fetch the submission by student name
            submission = get_object_or_404(ProjectSubmission, matriculation_number=matriculation_number,
                                           subject_code=subject_code)

            # Update the submission with the posted data
            submission.grade = request.POST.get('grade', '')
            submission.status = request.POST.get('status', '')
            submission.save()

            messages.success(request, 'Submission updated successfully!')
        except ProjectSubmission.DoesNotExist:
            messages.error(request, 'Submission not found.')

    return redirect('professor_dashboard')