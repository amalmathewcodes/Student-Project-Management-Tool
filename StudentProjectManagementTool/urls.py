from django.urls import path
from SPMT import views
from django.contrib import admin  # Add this import


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),  # This line enables the admin panel
    path('student_login/', views.student_login, name='student_login'),
    path('professor_login/', views.professor_login, name='professor_login'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('professor_dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('signup_view/', views.student_signup_view, name='signup_view'),
    path('logout/', views.logout_view, name='logout'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('submit_project/', views.submit_project, name='submit_project'),
    path('update_grade_status/<str:matriculation_number>/<str:subject_code>/', views.update_grade_status,name='update_grade_status'),

]
