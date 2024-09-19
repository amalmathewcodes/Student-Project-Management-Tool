from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import CustomUser,ProjectSubmission,Student
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)
User = get_user_model()  # Define User using get_user_model

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mobile_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'mobile_number', 'username', 'password1', 'password2', 'user_type')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }



class StudentSignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'First name is required.',
        }
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Last name is required.',
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
        }
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Mobile number is required.',
        }
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'mobile_number', 'username', 'password1', 'password2')
        widgets = {
            'user_type': forms.HiddenInput(),  # This will set the user_type as 'student' in the form
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'  # Set user_type to student before saving

        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                email=self.cleaned_data['email'],
                mobile_number=self.cleaned_data['mobile_number'],
            )

        return user


class StudentLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProfessorLoginForm(forms.Form):
    security_code = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProjectSubmissionForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ProjectSubmission
        fields = ['student_name', 'subject_name', 'subject_code', 'student', 'matriculation_number', 'remarks', 'submitted_to', 'file']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'matriculation_number': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'submitted_to': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }