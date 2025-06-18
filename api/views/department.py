from typing import Any, Dict, cast
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, authentication, permissions
from api.models import Department, Employee, PositionType
from api.serializers import DepartmentSerializer, EmployeeSerializer
from api.services.department import DepartmentService, DepartmentreateError
from api.services.employee import EmployeeCreateError, EmployeeService
import logging


logger = logging.getLogger(__name__)


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    service = DepartmentService()
    http_method_names = ["get", "delete", "post", "patch"]
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = DepartmentSerializer(data=request.data)

        if serializer.is_valid():
            # TODO: investigate why cast is needed here (Pylance error)
            validated_data = cast(Dict[str, Any], serializer.validated_data)

            try:
                employee = self.service.create(
                    validated_data.get("name", ""),
                    validated_data.get("description",  ""),
                    # validated_data.get("employees", []),
                )
                response_serializer = DepartmentSerializer(employee)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except DepartmentreateError as e:
                logger.error(e)
                return Response({"errors": [e.message]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
