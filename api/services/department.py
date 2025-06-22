from api.models import Department


class DepartmentService:

    def create(self, name: str, description: str) -> Department:
        """ Creates a new department. """
        department = Department.objects.create(
            name=name,
            description=description,
        )

        return department
