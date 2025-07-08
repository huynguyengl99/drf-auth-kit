Serializers
===========

.. module:: auth_kit.serializers

Authentication and user management serializers for DRF Auth Kit.

Login Serializers
-----------------

.. module:: auth_kit.serializers.login

.. autofunction:: auth_kit.serializers.login.get_login_serializer

.. module:: auth_kit.serializers.login_factors

.. autoclass:: auth_kit.serializers.login_factors.LoginRequestSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.login_factors.BaseLoginResponseSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.login_factors.JWTResponseSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.login_factors.TokenResponseSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: auth_kit.serializers.login_factors.get_login_response_serializer

JWT Serializers
---------------

.. module:: auth_kit.serializers.jwt

.. autoclass:: auth_kit.serializers.jwt.CookieTokenRefreshSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.jwt.JWTSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Token Serializers
-----------------

.. module:: auth_kit.serializers.token

.. autoclass:: auth_kit.serializers.token.TokenSerializer
   :members:
   :undoc-members:
   :show-inheritance:

User Serializers
----------------

.. module:: auth_kit.serializers.user

.. autoclass:: auth_kit.serializers.user.UserDetailsSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Registration Serializers
------------------------

.. module:: auth_kit.serializers.registration

.. autoclass:: auth_kit.serializers.RegisterSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.VerifyEmailSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.ResendEmailVerificationSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Password Serializers
--------------------

.. module:: auth_kit.serializers.password

.. autoclass:: auth_kit.serializers.PasswordChangeSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.PasswordResetSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.serializers.PasswordResetConfirmSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Logout Serializers
------------------

.. module:: auth_kit.serializers.logout

.. autoclass:: auth_kit.serializers.logout.AuthKitLogoutSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Custom Fields
-------------

.. module:: auth_kit.serializer_fields

.. autoclass:: auth_kit.serializer_fields.UnquoteStringField
   :members:
   :undoc-members:
   :show-inheritance:
