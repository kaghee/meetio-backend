
from typing import Any, Dict, cast
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions
from api.models import Employee, PositionType
from api.serializers import EmployeeSerializer, EmployeeUpdateSerializer
from api.services.employee import EmployeeCreateError, EmployeeService
import logging

logger = logging.getLogger(__name__)


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    service = EmployeeService()
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """ Endpoint to list all employees. If a filter string is provided,
        it will filter employees by email or name. """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        if "filter" in request.query_params:
            filter_string = request.query_params.get("filter", "")
            filtered_employees = [
                emp for emp in serializer.data
                if filter_string.lower() in emp["email"].lower()
                or filter_string.lower() in emp["name"].lower()
            ]
            if len(filtered_employees):
                return Response(filtered_employees, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"errors": ["No matches found."]}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.data, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        """ Endpoint to create a new employee. """
        serializer = self.get_serializer(data=request.data)
        department_id = request.data.get("department_id")

        if serializer.is_valid():
            # TODO: investigate why cast is needed here (Pylance error)
            validated_data = cast(Dict[str, Any], serializer.validated_data)

            try:
                employee = self.service.create(
                    validated_data.get("name", ""),
                    validated_data.get("email", ""),
                    validated_data.get("position", PositionType.EMPLOYEE),
                    department_id
                )
                response_serializer = self.get_serializer(employee)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except EmployeeCreateError as e:
                logger.error(e)
                return Response(
                    {"errors": [e.message]}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        """ Endpoint to update the fields of an employee. """
        employee = self.get_object()
        serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        """ Endpoint to delete an employee. """
        try:
            super().destroy(request, *args, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{e}")
            return Response(
                {"errors": [f"Cannot delete employee: {e}"]}, status=status.HTTP_409_CONFLICT
            )
