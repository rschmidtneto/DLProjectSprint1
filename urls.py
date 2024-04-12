
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    #path('',views.login_user, name='login'),
    path('logout/',views.logout_user, name='logout'),
    path('roster/', views.RoasterView.as_view(), name='roaster'),
    path('roster/booking/<int:pk>', views.viewBooking, name = 'booking'),
    path('edit/<int:pk>', views.editBooking, name = 'editBooking'),
    path('delete/<int:pk>', views.deleteBooking, name = 'deleteBooking'),
    path('addBooking/<int:jobId>/<str:date>/', views.addBooking, name = 'addBooking'),
    path('employees/', views.getEmployees, name = 'getEmployees'),
    path('getJobRoles/<int:pk>', views.getJobRoles, name = 'getJobRoles'),
    path('create/', views.createBooking, name = 'createBooking'),
    path('change-password/', views.change_password, name='change_password')

    
   
]