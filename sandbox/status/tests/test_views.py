from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class StatusViewTestCase(APITestCase):
    def test_get(self) -> None:
        url = reverse("status")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
