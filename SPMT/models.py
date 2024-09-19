from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')

class Student(models.Model):
    objects = None
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.student_name


class ProjectSubmission(models.Model):
    student_name = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=100)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject_code = models.CharField(max_length=20, default='')
    matriculation_number = models.CharField(max_length=20, default='')
    file = models.FileField(upload_to='submissions/')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='Pending')
    grade = models.CharField(max_length=10, blank=True, default='')
    remarks = models.TextField(blank=True, default='')
    submitted_to = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.subject_name} - {self.student.username}"