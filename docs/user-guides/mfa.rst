Multi-Factor Authentication (MFA)
==================================

This guide covers how to set up and use multi-factor authentication with DRF Auth Kit. MFA adds an extra layer of security by requiring users to provide a second form of verification in addition to their password.

Prerequisites
-------------

**API Documentation Setup Required**

Before following this guide, complete the :doc:`api-setup` to configure interactive API documentation (Swagger UI, ReDoc, and DRF Browsable API). This setup is essential for testing the MFA endpoints described below.

Overview
--------

DRF Auth Kit provides a comprehensive MFA system with:

- **Email-based MFA**: Send verification codes via email
- **Authenticator App MFA**: Generate QR codes for apps like Google Authenticator, Authy
- **Backup Codes**: Recovery codes for account access when primary method unavailable
- **Extensible System**: Add custom MFA methods
- **User Management**: Users can enable/disable and manage multiple MFA methods
- **API Integration**: Full REST API for MFA operations with interactive documentation

The MFA system is inspired by django-trench but simplified and better integrated with DRF Auth Kit's architecture.

Installation
------------

MFA support requires additional dependencies:

.. code-block:: bash

    pip install drf-auth-kit[mfa]

This installs **pyotp** (>=2.9.0) for TOTP (Time-based One-Time Password) generation and validation.

Configuration
-------------

**Enable MFA in Django Settings**

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ... your existing apps
        'auth_kit',
        'auth_kit.mfa',  # Add MFA support
    ]

    AUTH_KIT = {
        'USE_MFA': True,  # Enable MFA system
    }

**Run Migrations**

.. code-block:: bash

    python manage.py migrate

This creates the necessary database tables for MFA methods and backup codes.

**Explore MFA Endpoints**

Once enabled, visit your API documentation to see the new MFA endpoints (configured in the Prerequisites section above).


MFA Authentication Flow
-----------------------

When MFA is enabled, the login process becomes a two-step flow:

**Step 1: Username/Password Authentication**


1. User submits username/password to ``POST /api/auth/login/``
2. If credentials are valid and MFA is enabled, response includes:
   - ``ephemeral_token`` - Temporary token for MFA verification
   - ``method`` - Primary MFA method name
   - ``mfa_enabled: true`` - Indicates MFA is required

**Step 2: MFA Code Verification**


1. User receives MFA code (email or generates from app)
2. Submit to ``POST /api/auth/login/verify/`` with:
   - ``ephemeral_token`` - From step 1
   - ``code`` - MFA verification code or backup code
3. Response includes final authentication tokens and user data

**Additional MFA Endpoints**

During the MFA flow, these endpoints are available:

- ``POST /api/auth/login/change-method/`` - Switch between MFA methods
- ``POST /api/auth/login/resend/`` - Resend MFA code (email method)

Setting Up MFA Methods
-----------------------

**MFA Management Endpoints**

Once logged in, users can manage their MFA methods via:

- ``GET /api/auth/mfa/`` - List user's MFA methods
- ``POST /api/auth/mfa/`` - Create new MFA method
- ``POST /api/auth/mfa/confirm/`` - Confirm/activate new MFA method
- ``POST /api/auth/mfa/primary/`` - Set primary MFA method
- ``POST /api/auth/mfa/deactivate/`` - Deactivate MFA method
- ``POST /api/auth/mfa/delete/`` - Delete MFA method
- ``POST /api/auth/mfa/send/`` - Send MFA verification code

**Email MFA Setup**


1. Navigate to ``POST /api/auth/mfa/`` in your API documentation
2. Set ``method`` to ``"email"`` in the request body
3. Response includes setup confirmation and backup codes
4. User receives verification email with TOTP code
5. Use ``POST /api/auth/mfa/confirm/`` with ``method`` and ``code`` to activate

**Authenticator App Setup**


1. Navigate to ``POST /api/auth/mfa/`` in your API documentation
2. Set ``method`` to ``"app"`` in the request body
3. Response includes:
   - ``setup_data.qr_link`` - QR code URI for scanning
   - ``backup_codes`` - Recovery codes array
4. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
5. Use ``POST /api/auth/mfa/confirm/`` with ``method`` and ``code`` to activate

**Backup Codes**


Backup codes are automatically generated when setting up MFA:

- Use when primary MFA method is unavailable
- Each code can only be used once
- Generate new codes if running low
- Store securely (password manager recommended)

Managing MFA Methods
--------------------

**View Current Methods**


Use ``GET /api/auth/mfa/`` to see:

- ``name`` - MFA method name (e.g., "email", "app")
- ``is_active`` - Whether method is active
- ``is_primary`` - Whether method is the primary method
- ``is_setup`` - Whether method has been configured

**Setting Primary Method**


When multiple MFA methods exist:

1. Use ``POST /api/auth/mfa/primary/``
2. Set ``method`` to the method name (e.g., "email")
3. Include ``primary_code`` if required by settings
4. This method will be used by default during login

**Deactivating Methods**


Temporarily disable a method without deletion:

1. Use ``POST /api/auth/mfa/deactivate/``
2. Set ``method`` to the method name
3. Include ``code`` for verification
4. Method remains configured but won't be used

**Deleting Methods**


Permanently remove an MFA method:

1. Use ``POST /api/auth/mfa/delete/``
2. Set ``method`` to the method name
3. Include ``code`` if required by settings
4. Cannot delete the last active method (configurable)

Testing MFA Flow
----------------

**Using API Documentation**

The interactive API documentation makes testing MFA flows easy:

1. **Setup**: Create MFA methods using ``POST /api/auth/mfa/``
2. **Login**: Test two-step login process
3. **Management**: Try enabling/disabling methods
4. **Recovery**: Test backup code usage

**Common Test Scenarios**


Test these scenarios in your API documentation:

- First-time MFA setup
- Login with different MFA methods
- Switching between methods during login
- Using backup codes
- Managing multiple methods
- Error handling (invalid codes, expired tokens)

Configuration Options
---------------------

**MFA Security Settings**

.. code-block:: python

    AUTH_KIT = {
        'USE_MFA': True,

        # TOTP Configuration
        'MFA_TOTP_DEFAULT_INTERVAL': 30,        # Code validity (seconds)
        'MFA_TOTP_DEFAULT_VALID_WINDOW': 0,     # Clock skew tolerance

        # Backup Codes
        'NUM_OF_BACKUP_CODES': 5,               # Number of backup codes
        'BACKUP_CODE_LENGTH': 12,               # Backup code length
        'BACKUP_CODE_SECURE_HASH': True,        # Secure storage

        # Token Expiry
        'MFA_EPHEMERAL_TOKEN_EXPIRY': 900,      # 15 minutes

        # App Settings
        'MFA_APPLICATION_NAME': 'My App',       # Shown in authenticator apps

        # Security Constraints
        'MFA_PREVENT_DELETE_ACTIVE_METHOD': False,
        'MFA_PREVENT_DELETE_PRIMARY_METHOD': False,
        'MFA_DELETE_ACTIVE_METHOD_REQUIRE_CODE': False,
    }

**Available MFA Handlers**

.. code-block:: python

    AUTH_KIT = {
        'MFA_HANDLERS': [
            'auth_kit.mfa.handlers.app.MFAAppHandler',      # Authenticator apps
            'auth_kit.mfa.handlers.email.MFAEmailHandler',  # Email codes
            # Add custom handlers here
        ],
    }

Frontend Integration
--------------------

**Two-Step Login Flow**

.. code-block:: javascript

    // Step 1: Initial login
    async function login(username, password) {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.mfa_enabled) {
            // MFA required - show MFA form
            return { requiresMFA: true, ephemeralToken: data.ephemeral_token };
        } else {
            // No MFA - login complete
            return { requiresMFA: false, user: data.user };
        }
    }

    // Step 2: MFA verification
    async function verifyMFA(ephemeralToken, code) {
        const response = await fetch('/api/auth/login/verify/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ephemeral_token: ephemeralToken,
                code: code
            })
        });

        const data = await response.json();
        return data; // Contains final tokens and user data
    }

**MFA Method Management**

.. code-block:: javascript

    // Setup new MFA method
    async function setupMFA(method) {
        const response = await fetch('/api/auth/mfa/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ method: method })
        });

        const data = await response.json();

        if (method === 'app') {
            // Show QR code for scanning
            displayQRCode(data.qr_code);
        }

        return data;
    }

Advanced Topics
---------------

**Custom MFA Handlers**

You can create custom MFA methods by extending the base handler:

.. code-block:: python

    from auth_kit.mfa.handlers.base import MFABaseHandler

    class SMSMFAHandler(MFABaseHandler):
        name = "sms"

        def send_code(self, user, method):
            # Implement SMS sending logic
            pass

        def verify_code(self, user, method, code):
            # Implement SMS code verification
            pass

**Error Handling**

Common MFA error responses include:

- Invalid or expired ephemeral tokens
- Incorrect MFA codes
- Method setup failures
- Rate limiting errors

**Security Considerations**

- Use HTTPS in production for token security
- Set appropriate ephemeral token expiry times
- Educate users about backup code security
- Consider rate limiting for MFA attempts
- Monitor for suspicious MFA activity

Next Steps
----------

Now that you understand MFA implementation:

- **Test the Flow**: Use ``/api/docs/`` to test the complete MFA authentication flow
- **Customize Settings**: Adjust MFA configuration for your security requirements
- **User Education**: Help users understand MFA setup and backup codes
- **Monitor Usage**: Track MFA adoption and usage patterns
- **Social Authentication**: :doc:`social-authentication` - Combine with social login
- **Customization**: :doc:`customization` - Create custom MFA handlers
