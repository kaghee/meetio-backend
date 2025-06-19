from api.models import Appointment, Employee


class EmployeeNotFoundError(Exception):

    def __init__(self, message):
        self.message = message


class AppointmentService:

    def create(self, title: str, description: str, start_time: str, end_time: str, attendee_ids: list[int]) -> Appointment:

        attendees = []
        for att_id in attendee_ids:
            try:
                attendees.append(Employee.objects.get(id=att_id))
            except Employee.DoesNotExist:
                raise EmployeeNotFoundError(
                    f"Employee with id {att_id} not found.")

        appointment = Appointment.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )

        if attendee_ids:
            appointment.attendees.set(attendees)
            appointment.save()

        return appointment

    def validate_attendee_ids(self, attendee_ids: list[int]) -> None:
        for att_id in attendee_ids:
            if not Employee.objects.filter(id=att_id).exists():
                raise EmployeeNotFoundError(
                    f"Employee with id {att_id} not found.")
