"""
Views for the myapp module.

This module defines API views that handle HTTP requests and return appropriate
responses. It processes request data using the serializers defined in the
serializers module and returns responses in the requested format.
"""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_kit.myapp.serializers import MyModelSerializer


class MyView(APIView):
    """
    API view for handling MyModel data.

    This view processes POST requests containing MyModel data.
    It validates the incoming data using MyModelSerializer and
    returns the validated data as a response.

    Attributes:
        serializer_class (Serializer): The serializer class used for data validation.
    """

    serializer_class = MyModelSerializer

    def post(self, request: Request) -> Response:
        """
        Handle POST requests with MyModel data.

        This method validates the incoming request data using the serializer
        and returns the validated data.

        Args:
            request (Request): The HTTP request object containing the data.

        Returns:
            Response: A DRF Response object containing the validated data.

        Raises:
            ValidationError: If the request data fails validation.
        """
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
