from django.db import models


class PositionType(models.TextChoices):
    EMPLOYEE = "employee"
    MANAGER = "manager"


class Department(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)


class Employee(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    position = models.CharField(max_length=30, default=PositionType.EMPLOYEE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees', null=True, blank=True)

    def __str__(self):
        return self.name


Department.add_to_class('manager', models.OneToOneField(
    Employee,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='managed_department',
    limit_choices_to={'position': PositionType.MANAGER}
))


class Appointment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    attendees = models.ManyToManyField(Employee, related_name='appointments')

    def __str__(self):
        return f"{self.title} {self.start_time.strftime('%Y-%m-%d %H:%M')}"
