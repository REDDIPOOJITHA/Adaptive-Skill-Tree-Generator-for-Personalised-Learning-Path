
from django.urls import path
from AdminApp import views


urlpatterns = [
    path('', views.index),
    path('ALogAction',views.ALogAction),
    path('home', views.home),
    # path('addsubject', views.addsubject),
    # path('AddSubAction', views.AddSubAction),
    # path('AddQAnw', views.AddQAnw),
    # path('AddQAAction', views.AddQAAction),
    path('ViewQAnw', views.ViewQAnw),
    path('AddCareerSkills', views.AddCareerSkills),
    path('AddCareerAction', views.AddCareerAction),
    path('ViewStudents', views.ViewStudents),
    path('Addguidance', views.Addguidance),
    path('AddCAction', views.AddCAction),

]
