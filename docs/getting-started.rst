Getting Started
===============

This guide will help you get started with DRF Auth Kit quickly and easily.

Quick Setup
-----------

Basic Django Configuration
---------------------------

Add the required apps to ``INSTALLED_APPS`` and configure authentication:

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ... your existing apps
        'rest_framework',
        'allauth',             # Required
        'allauth.account',     # Required
        'auth_kit',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'auth_kit.authentication.JWTCookieAuthentication',
        ],
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }

    # AUTH_KIT uses sensible defaults (AUTH_TYPE='jwt', USE_AUTH_COOKIE=True)
    # Override only if needed

Include URLs and run migrations:

.. code-block:: python

    # urls.py
    urlpatterns = [
        path('api/auth/', include('auth_kit.urls')),
        # Your other URLs
    ]

.. code-block:: bash

    # Terminal
    python manage.py migrate

For detailed configuration options, see :doc:`configuration`.

Multi-Factor Authentication (MFA) Setup
----------------------------------------

**Enable MFA**: Add MFA support to your application:

.. code-block:: python

    # Add MFA to INSTALLED_APPS
    INSTALLED_APPS = [
        # ... your existing apps
        'auth_kit',
        'auth_kit.mfa',  # MFA functionality
    ]

    # Enable MFA in AUTH_KIT settings
    AUTH_KIT = {
        'USE_MFA': True,  # Enables MFA authentication flow
    }

    # Run migrations for MFA models
    # python manage.py migrate

**MFA Authentication Flow**: When MFA is enabled, the login process becomes two-step:

1. **Step 1**: ``POST /api/auth/login/`` - Username/password authentication
2. **Step 2**: ``POST /api/auth/login/verify/`` - MFA code verification

**Available MFA Methods**:

- **Email MFA**: Sends TOTP codes via email (requires email configuration)
- **Authenticator App**: Generates QR codes for Google Authenticator, Authy, etc.
- **Backup Codes**: Automatic generation of recovery codes

**Additional Endpoints**: When MFA is enabled, these endpoints become available:

- ``GET|POST /api/auth/mfa/`` - MFA method management
- ``POST /api/auth/login/change-method/`` - Change MFA method during login
- ``POST /api/auth/login/resend/`` - Resend MFA code

Social Authentication Setup
----------------------------

**Automatic URL Generation**: When you include ``auth_kit.social.urls``, the system automatically generates authentication URLs for any installed Django Allauth social providers. No need to manually define URLs for each provider.

**Provider Configuration**: Add social providers to ``INSTALLED_APPS`` and configure them in ``SOCIALACCOUNT_PROVIDERS``:

.. code-block:: python

    # Add social providers to INSTALLED_APPS
    INSTALLED_APPS = [
        # ... your existing apps
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',  # Google OAuth2
        'allauth.socialaccount.providers.github',  # GitHub OAuth2
        'auth_kit.social',  # DRF Auth Kit social integration
    ]

    # Configure social providers
    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': ['profile', 'email'],
            'AUTH_PARAMS': {'access_type': 'online'},
            'OAUTH_PKCE_ENABLED': True,
            'APP': {
                'client_id': 'your-google-client-id',
                'secret': 'your-google-client-secret',
            }
        },
    }

    # Include social URLs
    urlpatterns = [
        path('api/auth/', include('auth_kit.urls')),
        path('api/auth/social/', include('auth_kit.social.urls')),
    ]

API Documentation Setup
------------------------

DRF Auth Kit includes automatic OpenAPI schema generation. Set up DRF Spectacular to explore the API:

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ... your existing apps
        'drf_spectacular',
    ]

    SPECTACULAR_SETTINGS = {
        'TITLE': 'Your API Documentation',
        'DESCRIPTION': 'API documentation with authentication',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
    }

    # urls.py
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView,
    )

    urlpatterns = [
        # ... your existing URLs
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

Visit ``/api/docs/`` to explore the complete API documentation with all available authentication endpoints.

External Library Configuration
-------------------------------

For advanced configuration, refer to the official documentation:

- **Django REST Framework Simple JWT**: https://django-rest-framework-simplejwt.readthedocs.io/
- **Django Allauth**: https://docs.allauth.org/
- **DRF Spectacular**: https://drf-spectacular.readthedocs.io/

Next Steps
----------

- :doc:`user-guides/basic-usage` - Learn how to use the basic authentication features
- :doc:`user-guides/social-authentication` - Set up social authentication
- :doc:`user-guides/mfa` - Enable multi-factor authentication
- :doc:`user-guides/customization` - Customize the authentication flow
