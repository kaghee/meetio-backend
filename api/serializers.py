from api.models import Employee, Department, Appointment, PositionType
from rest_framework import serializers


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=30)
    position = serializers.ChoiceField(choices=PositionType.choices, default=Employee)

    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(max_length=30, required=False)
    position = serializers.ChoiceField(choices=PositionType.choices, default=Employee, required=False)

    class Meta:
        model = Employee
        fields = "__all__"


class DepartmentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    description = serializers.CharField()
    employees = EmployeeSerializer(many=True)

    class Meta:
        model = Department
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"
