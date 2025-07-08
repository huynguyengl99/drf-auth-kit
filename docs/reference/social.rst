Social Authentication
=====================

.. module:: auth_kit.social

Social authentication integration with Django Allauth.

Views
-----

Login Views
~~~~~~~~~~~

.. module:: auth_kit.social.views.login

.. autoclass:: auth_kit.social.views.login.SocialLoginView
   :members:
   :undoc-members:
   :show-inheritance:

Connection Views
~~~~~~~~~~~~~~~~

.. module:: auth_kit.social.views.connect

.. autoclass:: auth_kit.social.views.connect.SocialConnectView
   :members:
   :undoc-members:
   :show-inheritance:

Account Management Views
~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: auth_kit.social.views.account

.. autoclass:: auth_kit.social.views.account.SocialAccountViewSet
   :members:
   :undoc-members:
   :show-inheritance:

UI Views
~~~~~~~~

.. module:: auth_kit.social.views.ui

.. autoclass:: auth_kit.social.views.ui.SocialLoginTemplateView
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.social.views.ui.SocialAccountManagementView
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: auth_kit.social.views.ui.get_provider_icon

.. autofunction:: auth_kit.social.views.ui.get_provider_display_name

Serializers
-----------

Login Serializers
~~~~~~~~~~~~~~~~~

.. module:: auth_kit.social.serializers.login

.. autofunction:: auth_kit.social.serializers.login.get_social_login_serializer

.. autoclass:: auth_kit.social.serializers.login.SocialLoginWithTokenRequestSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: auth_kit.social.serializers.login.SocialLoginWithCodeRequestSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Account Serializers
~~~~~~~~~~~~~~~~~~~

.. module:: auth_kit.social.serializers.account

.. autoclass:: auth_kit.social.serializers.account.SocialAccountSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Connection Serializers
~~~~~~~~~~~~~~~~~~~~~~

.. module:: auth_kit.social.serializers.connect

.. autoclass:: auth_kit.social.serializers.connect.SocialConnectSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

.. module:: auth_kit.social.utils

.. autofunction:: auth_kit.social.utils.normalize_app_name

.. autofunction:: auth_kit.social.utils.get_social_login_callback_url

.. autofunction:: auth_kit.social.utils.get_social_connect_callback_url
