from typing import Any, Dict, cast
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, authentication, permissions
from api.models import Appointment, Employee
from api.serializers import AppointmentSerializer, AppointmentListSerializer
from api.services.appointment import AppointmentService, EmployeeNotFoundError


import logging


logger = logging.getLogger(__name__)


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    service = AppointmentService()
    http_method_names = ["get", "delete", "post", "patch"]
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """ Lists the departments.

        If a date is provided in the query, appointments are filtered
        by the date.
        If there are no matches, future dates are checked, and appointments
        for the earliest date are returned.

        Query param format: 2025-06-20. """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        if "date" in request.query_params:
            queried_date = request.query_params.get("date", "")
            response_serializer = AppointmentListSerializer

            # TODO: compare dates as date objects
            filtered_appointments = [app for app in serializer.data
                if app["start_time"][:10] == queried_date
            ]

            if len(filtered_appointments):
                resp_dict = {
                    "date": filtered_appointments[0]["start_time"][:10],
                    "appointments": filtered_appointments
                }
                return Response(response_serializer(resp_dict).data, status=status.HTTP_200_OK)

            # If no appointments match the queried date,
            # look for any future appointments. In case of matches,
            # return the matches' date in the response.
            elif (future_appointments := [app for app in serializer.data
                if app["start_time"][:10] > queried_date
            ]):
                resp_dict = {
                    "date": future_appointments[0]["start_time"][:10],
                    "appointments": future_appointments
                }
                return Response(response_serializer(resp_dict).data, status=status.HTTP_200_OK)

            else:
                return Response({"errors": ["No matches found."]}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
