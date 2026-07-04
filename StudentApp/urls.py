
from django.urls import path
from StudentApp import views

urlpatterns = [
    path('RegAction', views.RegAction),
    path('UserLogAction',views.UserLogAction),
    path('home', views.home),
    path('viewprofile', views.viewprofile),
    path('gotoquiz', views.gotoquiz),
    path('SubAction', views.SubAction),
    path('QizeAction', views.QizeAction),
    path('ViewResult', views.ViewResult),
    path('skillassessment', views.skillassessment),
    path('TimeUp', views.TimeUp),
    path('back', views.back),
    path('skillTree', views.skill_tree_view),
    path('guidance', views.guidance),

]
