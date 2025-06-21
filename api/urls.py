from rest_framework import routers
from rest_framework.authtoken import views
from django.contrib import admin
from django.urls import include, path
from api.views.appointment import AppointmentViewSet
from api.views.department import DepartmentViewSet
from api.views.employee import EmployeeViewSet

router = routers.DefaultRouter()
router.register(r'employee', EmployeeViewSet)
router.register(r'department', DepartmentViewSet)
router.register(r'appointment', AppointmentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token)
]