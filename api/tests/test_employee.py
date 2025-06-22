from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Employee, PositionType


User = get_user_model()

class EmployeeTests(APITestCase):
    fixtures = ["api/fixtures/test_data.json"]

    def setUp(self):
        """ Set up authenticated test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_get_all_employees(self):
        url = reverse('employee-list')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 6, "There are 6 employees in the fixture.")
        self.assertEqual(data[0]['name'], 'Michael Scott')
        self.assertEqual(data[0]['position'], 'manager')
        self.assertEqual(data[1]['name'], 'Dwight Schrute')
        self.assertEqual(data[1]['position'], 'employee')

    def test_get_employee_by_id(self):
        url = reverse('employee-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'Michael Scott')
        self.assertEqual(data['position'], 'manager')

    def test_create_employee_success(self):
        url = reverse('employee-list')
        payload = {
            'name': 'Kelly Kapoor',
            'email': 'kelly@dm.com',
            'position': PositionType.MANAGER,
            'department_id': 1
        }

        response = self.client.post(url, payload, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 7, "6 existing employees + 1 created")
        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['email'], payload['email'])
        self.assertEqual(data['position'], 'manager')
        self.assertEqual(data['department'], payload['department_id'])

    def test_create_employee_payload_error(self):
        url = reverse('employee-list')

        # Invalid position type
        payload = {
            'name': 'Kelly Kapoor',
            'email': 'kelly@dm.com',
            'position': 'gossip girl',
            'department_id': 1
        }

        response = self.client.post(url, payload, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('"gossip girl" is not a valid choice.' in data['position'][0])

    def test_create_employee_missing_field(self):
        url = reverse('employee-list')

        # Email field is missing
        payload = {
            'name': 'Kelly Kapoor',
            'position': PositionType.MANAGER,
            'department_id': 1
        }

        response = self.client.post(url, payload, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('This field is required.' in data['email'][0])

    def test_create_employee_invalid_department(self):
        url = reverse('employee-list')

        # Non-existent department
        payload = {
            'name': 'Kelly Kapoor',
            'email': 'kelly@dm.com',
            'position': PositionType.MANAGER,
            'department_id': 9999
        }

        response = self.client.post(url, payload, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errors'][0], 'Department 9999 not found.' )

    def test_update_employee_success(self):
        url = reverse('employee-detail', kwargs={'pk': 1})
        payload = {
            'email': 'bestboss@dm.com'
        }

        response = self.client.patch(url, payload, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['email'], payload['email'])

    def test_update_employee_invalid_id(self):
        url = reverse('employee-detail', kwargs={'pk': 9999})
        payload = {
            'email': 'rookie@dm.com'
        }

        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_employee_success(self):
        url = reverse('employee-detail', kwargs={'pk': 1})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 5, "6 existing employees - 1 deleted")

    def test_get_filtered_employees(self):
        url = f"{reverse('employee-list')}?filter=michael"
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Michael Scott')

    def test_get_filtered_employees_email_or_name(self):
        # Change Michael's name so only his email matches
        url = reverse('employee-detail', kwargs={'pk': 1})
        payload = {
            'name': 'Mich4el Scott'
        }
        response = self.client.patch(url, payload, format='json')
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], payload['name'])

        # Filter by email and name
        url = f"{reverse('employee-list')}?filter=ha"
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Jim Halpert')
        self.assertEqual(data[1]['email'], 'michael@dm.com')

    def test_get_filtered_employees_no_match(self):
        url = f"{reverse('employee-list')}?filter=gabe"
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data['errors'][0], 'No matches found.')
