import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Appointment, Employee


User = get_user_model()


class AppointmentTests(APITestCase):
    fixtures = ["api/fixtures/test_data.json"]

    def setUp(self):
        """ Set up authenticated test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_list_appointments(self):
        url = reverse('appointment-list')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['title'], 'Michael x Kevin')
        self.assertEqual(len(data[0]['attendees']), 2)
        self.assertEqual(len(data[1]['attendees']), 2)
        self.assertEqual(len(data[2]['attendees']), 5)

    def test_list_appointments_for_date(self):
        url = f"{reverse('appointment-list')}?date=2025-12-22"
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['appointments']), 1)
        self.assertEqual(data['appointments'][0]['title'], 'Christmas Party')
        self.assertEqual(len(data['appointments'][0]['attendees']), 5)

    def test_list_appointments_for_future_date(self):
        # Querying december 1
        url = f"{reverse('appointment-list')}?date=2025-12-01"
        response = self.client.get(url, format='json')
        data = response.json()

        # Next appointment is on dec 22
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['appointments']), 1)
        self.assertEqual(data['appointments'][0]['title'], 'Christmas Party')


    def test_create_appointment(self):
        url = reverse('appointment-list')
        data = {
            "title": "Mystery Meeting",
            "description": "Not telling.",
            "start_time": "2025-10-01T10:00:00Z",
            "end_time": "2025-10-01T11:00:00Z",
            "attendee_ids": [1, 2, 3, 4]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.get(title="Mystery Meeting")
        self.assertEqual(appointment.description, data['description'])
        self.assertEqual(appointment.start_time, datetime.datetime(
            2025, 10, 1, 10, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(appointment.attendees.count(), 4)

    def test_create_appointment_with_invalid_attendee(self):
        url = reverse('appointment-list')
        data = {
            "title": "X",
            "description": "Y",
            "start_time": "2025-10-01T10:00:00Z",
            "end_time": "2025-10-01T11:00:00Z",
            "attendee_ids": [999]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Employee with id 999 not found.",
                      response.json()['errors'])

    def test_update_appointment(self):
        url = reverse('appointment-detail', args=[1])
        data = {
            "title": "Updated Title",
            "attendee_ids": [2, 5]  # Original: 1, 4
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        appointment = Appointment.objects.get(pk=1)
        self.assertEqual(appointment.title, data['title'])
        self.assertEqual(appointment.attendees.count(), 2)
        names = [emp.name for emp in appointment.attendees.all()]
        self.assertEqual(names[0], "Dwight Schrute")
        self.assertEqual(names[1], "Jim Halpert")

    def test_update_appointment_with_invalid_attendee(self):
        # Check original attendees
        appointment = Appointment.objects.get(pk=1)
        names = [emp.name for emp in appointment.attendees.all()]
        self.assertEqual(names[0], "Michael Scott")
        self.assertEqual(names[1], "Kevin Malone")

        url = reverse('appointment-detail', args=[1])
        data = {
            "attendee_ids": [999]  # Invalid attendee
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Employee with id 999 not found.",
                      response.json()['errors'])

        # Check if attendees have not updated
        appointment = Appointment.objects.get(pk=1)
        names = [emp.name for emp in appointment.attendees.all()]
        self.assertEqual(names[0], "Michael Scott")
        self.assertEqual(names[1], "Kevin Malone")
