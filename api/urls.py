from rest_framework import routers
from django.contrib import admin
from django.urls import include, path
from api.views.department import DepartmentViewSet
from api.views.employee import EmployeeViewSet


router = routers.DefaultRouter()
router.register(r'employee', EmployeeViewSet)
router.register(r'department', DepartmentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]