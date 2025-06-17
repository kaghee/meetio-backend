from django.db import models


class PositionType(models.TextChoices):
    EMPLOYEE = "employee"
    MANAGER = "manager"


class Employee(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    position = models.CharField(max_length=30, default=PositionType.EMPLOYEE)


class Department(models.Model):
    name = models.CharField(max_length=30)
    manager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='managed_departments')
    description = models.TextField(blank=True, null=True)


class Appointment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='appointments')

    # def __str__(self):
    #     return self.title
