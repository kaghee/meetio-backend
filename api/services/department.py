from typing import Any, Dict
from api.models import Department


class DepartmentreateError(Exception):

    def __init__(self, message):
        self.message = message


class DepartmentService:
    def create(self, name: str, description: str) -> Department:

        department = Department.objects.create(
            name=name,
            description=description,
        )

        return department
