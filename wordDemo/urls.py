from django.urls import path

from .views import homePage,loginPage,registerPage , logOut , wordPage,userProfil,reset_password

urlpatterns = [

    path('',homePage,name="homePage"),

    path('login/',loginPage,name='loginPage'),

    path('register/',registerPage,name='registerPage'),

    path('logout/',logOut, name='logOut'),  # logOut adında bir URL şablonu tanımla

    path('wordPage/<int:number_question>/',wordPage , name='wordPage'),

    path('userProfil/',userProfil,name="userProfil"),

    path('userProfil/reset_password',reset_password,name='reset_password')


]
