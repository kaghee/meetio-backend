from api.models import Employee, Department, Appointment, PositionType
from rest_framework import serializers


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=30)
    position = serializers.ChoiceField(choices=PositionType.choices, default=Employee)

    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ["id", "name"]


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(max_length=30, required=False)
    position = serializers.ChoiceField(choices=PositionType.choices, default=Employee, required=False)

    class Meta:
        model = Employee
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)
    description = serializers.CharField()
    employees = EmployeeSerializer(many=True, required=False)

    class Meta:
        model = Department
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    # Displaying employee ids and names in api responses
    attendees = EmployeeNameSerializer(many=True, read_only=True)
    # Requiring employee ids in payloads
    attendee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Appointment
        fields = ["id", "title", "description",
                  "start_time", "end_time", "attendees", "attendee_ids"]
        read_only_fields = ["id", "attendees"]

class AppointmentListSerializer(serializers.Serializer):
    date = serializers.CharField()
    appointments = AppointmentSerializer(many=True)