from typing import Any, Dict, cast
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status, authentication, permissions
from api.models import Department, Employee
from api.serializers import DepartmentSerializer

import logging


logger = logging.getLogger(__name__)


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    http_method_names = ["get", "delete", "post", "patch"]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Endpoint for creating departments. """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # TODO: investigate why cast is needed here (Pylance error)
            validated_data = cast(Dict[str, Any], serializer.validated_data)

            try:
                department = self.service.create(
                    validated_data.get("name", ""),
                    validated_data.get("description",  ""),
                )
                response_serializer = self.get_serializer(department)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(e)
                return Response({"errors": [e.message]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """ Endpoint to update the fields of a department.
        The manager of the department can also be set here.
        """
        department = self.get_object()
        serializer = self.get_serializer(
            department, data=request.data, partial=True)

        if serializer.is_valid():

            try:
                serializer.save()

                manager_id = request.data.get("manager_id")
                if manager_id:
                    manager = Employee.objects.get(id=manager_id)
                    department.manager = manager
                    department.save()

                response_serializer = self.get_serializer(department)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            except Employee.DoesNotExist:
                return Response({"errors": [f"Manager with id {manager_id} not found."]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """ Endpoint to delete a department. """
        try:
            super().destroy(request, *args, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{e}")
            return Response({"errors": [f"Cannot delete department: {e}"]}, status=status.HTTP_409_CONFLICT)


    @action(detail=True, methods=['get'], url_path="employees")
    def list_employees(self, request, *args, **kwargs):
        """ Lists all the employees under a specific department. """
        department = self.get_object()
        employees = [{"id": emp.id, "name": emp.name} for emp in department.employees.all()]
        return Response(employees, status=status.HTTP_200_OK)
