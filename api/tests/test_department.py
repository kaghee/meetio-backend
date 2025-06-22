from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


User = get_user_model()

class DepartmentTests(APITestCase):
    fixtures = ["api/fixtures/test_data.json"]

    def setUp(self):
        """ Set up authenticated test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_list_departments(self):
        url = reverse('department-list')
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'Sales')
        self.assertEqual(data[1]['name'], 'Accounting')
        self.assertEqual(data[2]['name'], 'Warehouse')

    def test_list_employees(self):
        url = f"{reverse('department-detail', kwargs={'pk': 1})}employees/"
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3, "There are 3 sales employees in the fixture.")
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], 'Michael Scott')
        self.assertEqual(data[1]["name"], 'Dwight Schrute')
        self.assertEqual(data[2]["name"], 'Jim Halpert')
