Authentication
==============

.. module:: auth_kit.authentication

Core authentication classes and utilities for DRF Auth Kit.

Authentication Classes
----------------------

.. autoclass:: auth_kit.authentication.AuthKitCookieAuthentication
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.authentication.JWTCookieAuthentication
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.authentication.TokenCookieAuthentication
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.authentication.JWTCookieAuthenticationScheme
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.authentication.TokenCookieAuthenticationScheme
   :members:
   :undoc-members:
   :show-inheritance:

JWT Utilities
-------------

.. module:: auth_kit.jwt_auth

.. autofunction:: auth_kit.jwt_auth.set_auth_kit_cookie

.. autofunction:: auth_kit.jwt_auth.unset_jwt_cookies

.. autofunction:: auth_kit.jwt_auth.unset_token_cookie

.. autofunction:: auth_kit.jwt_auth.jwt_encode

Forms
-----

.. module:: auth_kit.forms

.. autoclass:: auth_kit.forms.AllAuthPasswordResetForm
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: auth_kit.forms.password_reset_url_generator
