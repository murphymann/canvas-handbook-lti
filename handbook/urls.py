from django.urls import path
from . import views

app_name = 'handbook'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('login/', views.lti_login, name='lti_login'),
    path('launch/', views.lti_launch, name='lti_launch'),
]