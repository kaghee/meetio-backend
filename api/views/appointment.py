from typing import Any, Dict, cast
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status, authentication, permissions
from api.models import Appointment, Employee
from api.serializers import AppointmentSerializer
from api.services.appointment import AppointmentService, EmployeeNotFoundError
from django.db import transaction

import logging


logger = logging.getLogger(__name__)


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    service = AppointmentService()
    http_method_names = ["get", "delete", "post", "patch"]
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Endpoint for creating appointments. """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # TODO: investigate why cast is needed here (Pylance error)
            validated_data = cast(Dict[str, Any], serializer.validated_data)

            try:
                appointment = self.service.create(
                    validated_data.get("title", ""),
                    validated_data.get("description",  ""),
                    validated_data.get("start_time",  ""),
                    validated_data.get("end_time",  ""),
                    validated_data.get("attendee_ids",  []),
                )
                response_serializer = AppointmentSerializer(
                    # response_serializer = AppointmentResponseSerializer(
                    appointment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except EmployeeNotFoundError as e:
                logger.error(e)
                return Response({"errors": [e.message]}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(e)
                return Response({"errors": [e]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """ Endpoint to update the fields of an appointment. """
        appointment = self.get_object()
        serializer = self.get_serializer(
            appointment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            attendee_ids = request.data.get("attendee_ids")
            if attendee_ids:
                try:
                    self.service.validate_attendee_ids(attendee_ids)

                    appointment.attendees.clear()
                    for attendee_id in attendee_ids:
                        attendee = Employee.objects.get(id=attendee_id)
                        appointment.attendees.add(attendee)
                    appointment.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)

                except EmployeeNotFoundError as e:
                    logger.error(e)
                    return Response({"errors": [e.message]}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """ Endpoint to delete an appointment. """
        try:
            super().destroy(request, *args, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{e}")
            return Response({"errors": [f"Cannot delete appointment: {e}"]}, status=status.HTTP_409_CONFLICT)
