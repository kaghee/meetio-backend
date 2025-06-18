from typing import Any, Dict
from api.models import Department, Employee, PositionType


class EmployeeCreateError(Exception):

    def __init__(self, message):
        self.message = message


class EmployeeService:
    """Service class for Employees."""

    def create(self, name: str, email: str, position: PositionType, department_id: int) -> Employee:
        """Creates a new employee. Throws an error if the department does not exist."""

        try:
            Department.objects.get(id=department_id)

            employee = Employee.objects.create(
                name=name,
                email=email,
                position=position,
                department_id=department_id
            )
        except Department.DoesNotExist:
            raise EmployeeCreateError(f"Department {department_id} not found.")

        return employee
