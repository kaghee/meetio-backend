from api.models import Department


class DepartmentService:
    def create(self, name: str, description: str) -> Department:

        department = Department.objects.create(
            name=name,
            description=description,
        )

        return department
