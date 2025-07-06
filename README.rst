DRF AUTH KIT
============

.. image:: https://img.shields.io/pypi/v/drf-auth-kit
   :target: https://pypi.org/project/drf-auth-kit/
   :alt: PyPI

.. image:: https://codecov.io/gh/forthecraft/drf-auth-kit/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/forthecraft/drf-auth-kit
   :alt: Code Coverage

.. image:: https://github.com/forthecraft/drf-auth-kit/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/forthecraft/drf-auth-kit/actions/workflows/test.yml
   :alt: Test

.. image:: https://www.mypy-lang.org/static/mypy_badge.svg
   :target: https://mypy-lang.org/
   :alt: Checked with mypy

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :target: https://microsoft.github.io/pyright/
   :alt: Checked with pyright

.. image:: https://drf-auth-kit.readthedocs.io/en/latest/_static/interrogate_badge.svg
   :target: https://github.com/forthecraft/drf-auth-kit
   :alt: Docstring

Modern Django REST Framework authentication toolkit with JWT cookies, social login, and comprehensive user management.

Features
--------

🔐 **Multiple Authentication Types**
   - JWT tokens with automatic refresh
   - DRF token authentication
   - Custom authentication support

🍪 **Cookie-Based Security**
   - Secure HTTP-only cookies
   - Automatic token management
   - CSRF protection

📧 **Complete User Management**
   - User registration with email verification
   - Password reset and change
   - Email verification workflows

🔧 **Flexible Configuration**
   - Multiple authentication backends
   - Customizable serializers and views
   - Django Allauth integration

🚀 **Developer Experience**
   - Full type hints support
   - Comprehensive test coverage
   - Auto-generated API documentation

Installation
------------

.. code-block:: bash

    pip install drf-auth-kit

Quick Start
-----------

1. Add to your Django settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ... your apps
        'rest_framework',
        'allauth',
        'allauth.account',
        'auth_kit',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'auth_kit.authentication.AuthKitAuthentication',
        ],
    }

    AUTH_KIT = {
        'AUTH_TYPE': 'jwt',  # or 'token' or 'custom'
        'USE_AUTH_COOKIE': True,
    }

2. Include Auth Kit URLs:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        path('api/auth/', include('auth_kit.urls')),
        # ... your other URLs
    ]

3. Run migrations:

.. code-block:: bash

    python manage.py migrate

Authentication Types
--------------------

**JWT Authentication (Recommended)**
   - Access and refresh tokens
   - Automatic token refresh
   - Secure cookie storage

**DRF Token Authentication**
   - Simple token-based auth
   - Compatible with DRF TokenAuthentication
   - Cookie support available

**Custom Authentication**
   - Bring your own authentication backend
   - Full customization support
   - Integrate with third-party services

API Endpoints
-------------

The package provides these authentication endpoints:

- ``POST /auth/login/`` - User authentication
- ``POST /auth/logout/`` - User logout
- ``POST /auth/registration/`` - User registration
- ``POST /auth/password/reset/`` - Password reset request
- ``POST /auth/password/reset/confirm/`` - Password reset confirmation
- ``POST /auth/password/change/`` - Password change
- ``GET/PUT/PATCH /auth/user/`` - User profile management
- ``POST /auth/registration/verify-email/`` - Email verification
- ``POST /auth/token/refresh/`` - JWT token refresh (JWT mode only)

Documentation
-------------

Please visit `DRF Auth Kit docs <https://drf-auth-kit.readthedocs.io/>`_ for complete documentation, including:

- Detailed configuration options
- Custom serializer examples
- Advanced usage patterns
- Integration guides

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.
