from django.urls import path
from . import views

urlpatterns = [
    path('', views.verification_home, name='verification'),
    path('procedures/', views.select_procedure, name='procedures'),
    path('results/', views.verification_results, name='verification_results'),
    path('<str:procedure_name>/', views.procedure_steps, name='procedure_steps'),
    path('<str:procedure_name>/preconditions/', views.procedure_preconditions, name='procedure_preconditions'),
    path('<str:procedure_name>/<int:step_number>/', views.procedure_steps, name='procedure_step'),
]