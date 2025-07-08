Customization
=============

This guide covers how to customize DRF Auth Kit to fit your specific needs. To effectively customize the system, you first need to understand the underlying authentication flow architecture.

Understanding the Authentication Flow
-------------------------------------

DRF Auth Kit uses a sophisticated **serializer composition pattern** that separates credential validation from token generation, enabling maximum flexibility and reusability.

Core Architecture: Request-Response Serializer Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The authentication system is built on three types of serializers:

**Request Serializers (Input Validation)**
    Handle credential validation and user authentication:

    - ``LoginRequestSerializer`` - Validates username/password credentials
    - ``SocialLoginRequestSerializer`` - Validates OAuth tokens/codes
    - **Key Method**: ``validate()`` - authenticates user and sets ``context["user"]``

**Response Serializers (Output Generation)**
    Generate authentication tokens from authenticated users:

    - ``JWTResponseSerializer`` - Generates JWT access/refresh tokens
    - ``TokenResponseSerializer`` - Generates DRF authentication tokens
    - **Key Method**: ``validate()`` - uses ``context["user"]`` to create tokens

**Final Serializers (Request + Response Combined)**
    Inherit from both to create complete authentication flows:

.. code-block:: python

    class LoginSerializer(
        JWTResponseSerializer,    # First parent - token generation
        LoginRequestSerializer    # Second parent - credential validation
    ):
        pass

The Magic: Method Resolution Order Chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The authentication flow works through Python's Method Resolution Order (MRO):

.. code-block:: python

    # When LoginSerializer.validate() is called:
    # 1. JWTResponseSerializer.validate() calls super().validate()
    # 2. LoginRequestSerializer.validate() authenticates user
    # 3. JWTResponseSerializer.validate() generates JWT tokens
    # 4. Returns: {"user": user_obj, "access": "jwt_token", "refresh": "jwt_token"}

**Flow Steps:**

1. **Credential Validation**: Request serializer authenticates user and stores in ``context["user"]``
2. **Token Generation**: Response serializer uses authenticated user to generate tokens
3. **Combined Output**: Final result contains both user data and authentication tokens

MFA Flow: Adding Intermediate Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multi-Factor Authentication extends the basic flow with **ephemeral tokens**:

**Step 1 - Credential Validation + MFA Check:**

.. code-block:: python

    class MFAFirstStepSerializer(
        MFAFirstStepResponseSerializer,  # Generates ephemeral token OR full auth
        LoginRequestSerializer           # Validates credentials
    ):
        pass

- **Input**: Username/password
- **Output**: Ephemeral token (if MFA required) OR full authentication (if MFA disabled)

**Step 2 - MFA Verification + Token Generation:**

.. code-block:: python

    class MFASecondStepSerializer(
        LoginResponseSerializer,        # Generates final auth tokens
        MFASecondStepRequestSerializer  # Validates ephemeral token + MFA code
    ):
        pass

- **Input**: Ephemeral token + MFA verification code
- **Output**: Full authentication tokens (same as standard login)

**Ephemeral Token System:**
    Temporary, short-lived tokens that prove first-step authentication completed, carrying user identity and MFA method information securely between steps.

Social Authentication: Reusing Response Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Social authentication demonstrates the power of the composition pattern:

.. code-block:: python

    class SocialLoginSerializer(
        LoginResponseSerializer,        # Same token generation as regular login
        SocialLoginRequestSerializer   # OAuth-specific credential validation
    ):
        pass

**Key Benefits:**

- **Reuses Response Logic**: Same token generation across all authentication methods
- **Custom Request Logic**: OAuth token/code validation instead of password validation
- **Consistent Output**: Social login returns identical token structure as regular login

Dynamic Serializer Factory Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system uses factory functions for runtime composition based on configuration:

.. code-block:: python

    def get_login_serializer():
        # Choose response serializer based on AUTH_TYPE setting
        if auth_kit_settings.AUTH_TYPE == 'jwt':
            response_serializer = JWTResponseSerializer
        elif auth_kit_settings.AUTH_TYPE == 'token':
            response_serializer = TokenResponseSerializer
        else:
            response_serializer = CustomResponseSerializer

        # Compose final serializer
        return type('LoginSerializer', (response_serializer, LoginRequestSerializer), {})

This enables **configuration-driven composition** where settings determine which serializers are combined.

Customization Philosophy
------------------------

Understanding this architecture enables powerful customization strategies:

**Modularity**
    Replace specific components without affecting others:

    - Custom request serializers for different authentication backends
    - Custom response serializers for different token formats
    - Custom composition for entirely new authentication flows

**Extensibility**
    Add new functionality by extending existing patterns:

    - Additional validation steps in request serializers
    - Extra fields in response serializers
    - Multi-step flows like MFA

**Reusability**
    Share common logic across different authentication methods:

    - Same token generation for multiple input methods
    - Same validation logic for multiple token types
    - Mix and match any request with any response serializer

Customization Examples
----------------------

Now that you understand the architecture, here are practical examples of how to customize different parts of the system.

Custom Request Serializers (Input Validation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Example 1: Custom Credential Validation**

Add business logic to credential validation:

.. code-block:: python

    # serializers.py
    from auth_kit.serializers import LoginRequestSerializer
    from rest_framework import serializers
    from django.contrib.auth import authenticate
    from myapp.models import UserProfile

    class CustomLoginRequestSerializer(LoginRequestSerializer):
        company_code = serializers.CharField(required=True)

        def validate(self, attrs):
            # Custom business logic before authentication
            company_code = attrs.get('company_code')
            if not UserProfile.objects.filter(company_code=company_code).exists():
                raise serializers.ValidationError('Invalid company code')

            # Call parent validation to authenticate user
            attrs = super().validate(attrs)

            # Additional checks after authentication
            user = self.context['user']
            if not user.profile.company_code == company_code:
                raise serializers.ValidationError('User not associated with this company')

            return attrs

**Example 2: API Key Authentication**

Replace password authentication with API key:

.. code-block:: python

    from auth_kit.serializers import BaseLoginRequestSerializer
    from django.contrib.auth import get_user_model
    from rest_framework import serializers

    User = get_user_model()

    class APIKeyRequestSerializer(BaseLoginRequestSerializer):
        api_key = serializers.CharField()

        def validate(self, attrs):
            api_key = attrs.get('api_key')

            try:
                user = User.objects.get(profile__api_key=api_key, is_active=True)
                self.context['user'] = user  # Set authenticated user in context
                return attrs
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid API key')

Custom Response Serializers (Output Generation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Example 1: Custom Token Format**

Add custom fields to authentication response:

.. code-block:: python

    from auth_kit.serializers import JWTResponseSerializer
    from rest_framework import serializers

    class CustomJWTResponseSerializer(JWTResponseSerializer):
        permissions = serializers.SerializerMethodField()
        company_info = serializers.SerializerMethodField()

        def get_permissions(self, obj):
            user = self.context['user']
            return list(user.get_all_permissions())

        def get_company_info(self, obj):
            user = self.context['user']
            return {
                'company_name': user.profile.company.name,
                'company_code': user.profile.company_code,
            }

**Example 2: Custom Token Backend**

Create entirely custom token system:

.. code-block:: python

    from auth_kit.serializers import BaseLoginResponseSerializer
    from rest_framework import serializers
    import jwt
    from datetime import datetime, timedelta

    class CustomTokenResponseSerializer(BaseLoginResponseSerializer):
        custom_token = serializers.SerializerMethodField()
        expires_at = serializers.SerializerMethodField()

        def get_custom_token(self, obj):
            user = self.context['user']
            payload = {
                'user_id': user.id,
                'username': user.username,
                'company_code': user.profile.company_code,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            return jwt.encode(payload, 'your-secret-key', algorithm='HS256')

        def get_expires_at(self, obj):
            return datetime.utcnow() + timedelta(hours=24)

Custom Final Serializers (Complete Flows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Example 1: Combine Custom Request + Response**

.. code-block:: python

    class CustomLoginSerializer(
        CustomJWTResponseSerializer,     # Custom token generation
        CustomLoginRequestSerializer    # Custom credential validation
    ):
        """
        Complete custom login flow with company validation and enhanced tokens.
        """
        pass

**Example 2: Multi-Step Custom Flow**

Create a flow similar to MFA but for different purposes:

.. code-block:: python

    class TwoFactorEmailSerializer(
        EmailVerificationResponseSerializer,  # Generates verification token
        LoginRequestSerializer                # Standard credential validation
    ):
        """Step 1: Validate credentials, send email verification."""
        pass

    class TwoFactorEmailVerifySerializer(
        CustomJWTResponseSerializer,         # Final token generation
        EmailVerificationRequestSerializer  # Validates email verification code
    ):
        """Step 2: Validate email code, generate final tokens."""
        pass

Configuration Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

**Register Custom Serializers**

Use settings to integrate your custom serializers:

.. code-block:: python

    # settings.py
    AUTH_KIT = {
        'AUTH_TYPE': 'custom',

        # Custom serializer classes
        'LOGIN_REQUEST_SERIALIZER': 'myapp.serializers.CustomLoginRequestSerializer',
        'LOGIN_RESPONSE_SERIALIZER': 'myapp.serializers.CustomJWTResponseSerializer',

        # Or override the complete serializer
        'LOGIN_SERIALIZER': 'myapp.serializers.CustomLoginSerializer',

        # Custom authentication class if needed
        'AUTHENTICATION_CLASS': 'myapp.authentication.CustomAuthentication',
    }

**Factory Function Override**

For more complex customization, override the factory functions:

.. code-block:: python

    # app_settings.py or serializers.py
    from auth_kit.app_settings import auth_kit_settings

    def custom_login_serializer_factory():
        """Custom factory that chooses serializers based on request or user type."""
        # You can inspect request context here
        if some_condition:
            return CustomLoginSerializer
        else:
            return StandardLoginSerializer

    # Override in settings
    AUTH_KIT = {
        'LOGIN_SERIALIZER_FACTORY': 'myapp.serializers.custom_login_serializer_factory',
    }

Additional Customization Examples
---------------------------------

Registration Serializer
~~~~~~~~~~~~~~~~~~~~~~~~

Registration doesn't use the request-response pattern, so it's customized directly:

.. code-block:: python

    # serializers.py
    from auth_kit.serializers import RegisterSerializer
    from rest_framework import serializers
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class CustomRegisterSerializer(RegisterSerializer):
        first_name = serializers.CharField(required=True, max_length=30)
        last_name = serializers.CharField(required=True, max_length=30)
        phone_number = serializers.CharField(required=False, max_length=20)

        def validate_phone_number(self, value):
            if value and not value.startswith('+'):
                raise serializers.ValidationError("Phone number must start with '+'")
            return value

        def save(self, request):
            user = super().save(request)
            user.first_name = self.validated_data.get('first_name')
            user.last_name = self.validated_data.get('last_name')
            user.save()

            # Create user profile with additional data
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                phone_number=self.validated_data.get('phone_number', '')
            )

            return user

Configure it in settings:

.. code-block:: python

    AUTH_KIT = {
        'REGISTER_SERIALIZER': 'myapp.serializers.CustomRegisterSerializer',
    }

User Detail Serializer
~~~~~~~~~~~~~~~~~~~~~~

Customize user profile serialization:

.. code-block:: python

    # serializers.py
    from auth_kit.serializers import UserDetailsSerializer
    from rest_framework import serializers
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class CustomUserDetailsSerializer(UserDetailsSerializer):
        full_name = serializers.SerializerMethodField()
        avatar = serializers.SerializerMethodField()
        phone_number = serializers.CharField(source='profile.phone_number', read_only=True)
        is_premium = serializers.BooleanField(source='profile.is_premium', read_only=True)

        class Meta(UserDetailsSerializer.Meta):
            fields = UserDetailsSerializer.Meta.fields + [
                'full_name', 'avatar', 'phone_number', 'is_premium'
            ]

        def get_full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}".strip()

        def get_avatar(self, obj):
            if hasattr(obj, 'profile') and obj.profile.avatar:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.profile.avatar.url)
            return None

        def update(self, instance, validated_data):
            # Handle nested profile updates
            profile_data = validated_data.pop('profile', {})

            # Update user fields
            instance = super().update(instance, validated_data)

            # Update profile fields
            if profile_data:
                profile = instance.profile
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()

            return instance

Configure it in settings:

.. code-block:: python

    AUTH_KIT = {
        'USER_DETAILS_SERIALIZER': 'myapp.serializers.CustomUserDetailsSerializer',
    }

Custom Views
------------

Custom Registration View
~~~~~~~~~~~~~~~~~~~~~~~~

Override the registration view for custom logic:

.. code-block:: python

    # views.py
    from auth_kit.views import RegisterView
    from rest_framework.response import Response
    from rest_framework import status
    from django.core.mail import send_mail
    from django.conf import settings

    class CustomRegisterView(RegisterView):
        def create(self, request, *args, **kwargs):
            # Call parent create method
            response = super().create(request, *args, **kwargs)

            # Custom logic after user creation
            if response.status_code == status.HTTP_201_CREATED:
                user = response.data.get('user')

                # Send welcome email
                send_mail(
                    subject='Welcome to Our Platform!',
                    message=f'Welcome {user["first_name"]}! Your account has been created successfully.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user['email']],
                    fail_silently=True
                )

                # Log user registration
                import logging
                logger = logging.getLogger('auth_kit')
                logger.info(f'New user registered: {user["email"]}')

            return response

        def get_response_data(self, user):
            # Customize response data
            data = super().get_response_data(user)
            data['welcome_message'] = 'Welcome to our platform!'
            return data

Configure it in settings:

.. code-block:: python

    AUTH_KIT = {
        'REGISTER_VIEW': 'myapp.views.CustomRegisterView',
    }

Custom Login View
~~~~~~~~~~~~~~~~~

Override the login view for custom authentication logic:

.. code-block:: python

    # views.py
    from auth_kit.views import LoginView
    from rest_framework.response import Response
    from rest_framework import status
    from django.utils import timezone
    from django.contrib.auth import login

    class CustomLoginView(LoginView):
        def login(self):
            # Call parent login method
            response = super().login()

            # Custom logic after login
            if hasattr(self, 'user'):
                # Update last login time
                self.user.last_login = timezone.now()
                self.user.save()

                # Log user activity
                from .models import UserActivity
                UserActivity.objects.create(
                    user=self.user,
                    action='login',
                    ip_address=self.get_client_ip(),
                    user_agent=self.request.META.get('HTTP_USER_AGENT', '')
                )

            return response

        def get_client_ip(self):
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = self.request.META.get('REMOTE_ADDR')
            return ip

        def get_response_data(self, user):
            # Customize response data
            data = super().get_response_data(user)
            data['last_login'] = user.last_login.isoformat() if user.last_login else None
            data['login_count'] = user.activity_set.filter(action='login').count()
            return data

Configure it in settings:

.. code-block:: python

    AUTH_KIT = {
        'LOGIN_VIEW': 'myapp.views.CustomLoginView',
    }

Custom Password Reset View
~~~~~~~~~~~~~~~~~~~~~~~~~~

Override password reset functionality:

.. code-block:: python

    # views.py
    from auth_kit.views import PasswordResetView
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings

    class CustomPasswordResetView(PasswordResetView):
        def send_reset_email(self, user, reset_url):
            # Custom email template and logic
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Your Site Name',
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }

            html_message = render_to_string('auth/password_reset_email.html', context)
            text_message = render_to_string('auth/password_reset_email.txt', context)

            send_mail(
                subject='Password Reset Request',
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            # Log password reset request
            import logging
            logger = logging.getLogger('auth_kit')
            logger.info(f'Password reset requested for user: {user.email}')

Configure it in settings:

.. code-block:: python

    AUTH_KIT = {
        'PASSWORD_RESET_VIEW': 'myapp.views.CustomPasswordResetView',
    }

Custom Email Templates
-----------------------

Email Template Customization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since DRF Auth Kit is API-based, the main template customization you'll need is for authentication emails. DRF Auth Kit uses Django Allauth's email templates.

**Available Email Templates**

Create these templates in your Django project to customize emails:

.. code-block:: text

    templates/
    └── account/
        └── email/
            ├── email_confirmation_subject.txt     # Email verification subject
            ├── email_confirmation_message.txt     # Email verification body
            ├── password_reset_key_subject.txt     # Password reset subject
            └── password_reset_key_message.txt     # Password reset body

**Simple Example**

.. code-block:: text

    <!-- templates/account/email/email_confirmation_message.txt -->
    Hello {{ user.first_name }},

    Please confirm your email address by clicking this link:
    {{ activate_url }}

    Thanks,
    The {{ site_name }} Team

**Template Configuration**

.. code-block:: python

    # settings.py
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            # ... other template settings
        },
    ]

**External Resources**

For comprehensive email template customization:

- `Django Allauth Email Templates <https://docs.allauth.org/en/latest/account/configuration.html#email-templates>`_ - Complete template reference
- `Email Template Examples <https://github.com/pennersr/django-allauth/tree/master/allauth/templates/account/email>`_ - Default templates on GitHub
- `Django Email Documentation <https://docs.djangoproject.com/en/stable/topics/email/>`_ - Email configuration guide

**Template Variables**

Common variables available in email templates:

- ``{{ user }}`` - User object
- ``{{ site_name }}`` - Site name
- ``{{ activate_url }}`` - Email confirmation URL
- ``{{ password_reset_url }}`` - Password reset URL

Advanced Customization
----------------------

Custom User Model
~~~~~~~~~~~~~~~~~

Use a custom user model with DRF Auth Kit:

.. code-block:: python

    # models.py
    from django.contrib.auth.models import AbstractUser
    from django.db import models

    class CustomUser(AbstractUser):
        email = models.EmailField(unique=True)
        phone_number = models.CharField(max_length=20, blank=True)
        date_of_birth = models.DateField(null=True, blank=True)
        is_premium = models.BooleanField(default=False)

        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = ['username']

        def __str__(self):
            return self.email

Configure it in settings:

.. code-block:: python

    # settings.py
    AUTH_USER_MODEL = 'myapp.CustomUser'

Custom Permissions
~~~~~~~~~~~~~~~~~~

Add custom permissions to authentication views:

.. code-block:: python

    # permissions.py
    from rest_framework.permissions import BasePermission

    class IsPremiumUser(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.is_premium

    class IsOwnerOrReadOnly(BasePermission):
        def has_object_permission(self, request, view, obj):
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            return obj.user == request.user

Use custom permissions in views:

.. code-block:: python

    # views.py
    from auth_kit.views import UserDetailsView
    from .permissions import IsPremiumUser

    class CustomUserDetailsView(UserDetailsView):
        permission_classes = [IsPremiumUser]

        def get_queryset(self):
            return super().get_queryset().filter(is_premium=True)

Custom Middleware
~~~~~~~~~~~~~~~~~

Add custom middleware for authentication:

.. code-block:: python

    # middleware.py
    from django.utils.deprecation import MiddlewareMixin
    import logging

    class AuthenticationLoggingMiddleware(MiddlewareMixin):
        def process_request(self, request):
            if request.path.startswith('/api/auth/'):
                logger = logging.getLogger('auth_kit')
                logger.info(f'Auth request: {request.method} {request.path} from {request.META.get("REMOTE_ADDR")}')

        def process_response(self, request, response):
            if request.path.startswith('/api/auth/'):
                logger = logging.getLogger('auth_kit')
                logger.info(f'Auth response: {response.status_code} for {request.path}')
            return response

Configure it in settings:

.. code-block:: python

    # settings.py
    MIDDLEWARE = [
        # ... other middleware
        'myapp.middleware.AuthenticationLoggingMiddleware',
    ]


Testing Custom Components
-------------------------

Testing Custom Serializers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.test import TestCase
    from rest_framework.test import APIRequestFactory
    from myapp.serializers import CustomRegisterSerializer

    class CustomSerializerTestCase(TestCase):
        def setUp(self):
            self.factory = APIRequestFactory()

        def test_custom_register_serializer(self):
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': '+1234567890'
            }

            request = self.factory.post('/api/auth/registration/', data)
            serializer = CustomRegisterSerializer(data=data)
            serializer.context['request'] = request

            self.assertTrue(serializer.is_valid())
            user = serializer.save(request)

            self.assertEqual(user.first_name, 'Test')
            self.assertEqual(user.last_name, 'User')
            self.assertTrue(hasattr(user, 'profile'))
            self.assertEqual(user.profile.phone_number, '+1234567890')

Testing Custom Views
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.test import TestCase
    from rest_framework.test import APIClient
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class CustomViewTestCase(TestCase):
        def setUp(self):
            self.client = APIClient()
            self.user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )

        def test_custom_login_view(self):
            response = self.client.post('/api/auth/login/', {
                'username': 'testuser',
                'password': 'testpass123'
            })

            self.assertEqual(response.status_code, 200)
            self.assertIn('access_token', response.data)
            self.assertIn('login_count', response.data)

            # Check that user activity was logged
            from myapp.models import UserActivity
            activity = UserActivity.objects.filter(
                user=self.user,
                action='login'
            ).first()
            self.assertIsNotNone(activity)

Best Practices
--------------

1. **Type Hints**: Always include type hints in custom components
2. **Documentation**: Document custom components for OpenAPI schema
3. **Testing**: Write tests for all custom components
4. **Backwards Compatibility**: Ensure customizations don't break existing functionality
5. **Security**: Follow security best practices in custom authentication logic
6. **Performance**: Consider performance impact of custom components
7. **Logging**: Add appropriate logging for debugging and monitoring

Next Steps
----------

Now that you understand DRF Auth Kit's architecture and customization capabilities:

**Understanding the Architecture**
    The key to effective customization is understanding the request-response serializer composition pattern and how the Method Resolution Order creates the authentication flow.

**Start Simple**
    Begin with simple customizations like adding fields to response serializers or custom validation in request serializers before attempting complex multi-step flows.

**Advanced Customization**
    For complex requirements, you can create entirely new authentication flows by composing custom request and response serializers, following the same patterns used by MFA and social authentication.

**Further Learning**

- **Source Code**: Review the DRF Auth Kit source code to see more examples of the composition pattern
- **MFA Implementation**: Study the MFA module to understand multi-step authentication flows
- **Social Authentication**: Examine the social authentication module to see how it reuses response serializers
- **Contribution**: Consider contributing useful custom components back to the project

**Key Takeaway**
    The serializer composition architecture enables you to customize any part of the authentication flow while maintaining compatibility and reusing existing components. Understanding this pattern unlocks the full power of DRF Auth Kit's flexibility.
