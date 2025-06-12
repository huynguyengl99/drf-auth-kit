from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class MyAppTestCase(APITestCase):
    def test_post(self) -> None:
        request_data = {"payload": "hello"}
        response = self.client.post(reverse("myapp"), data=request_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == request_data
