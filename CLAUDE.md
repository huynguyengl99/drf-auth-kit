# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DRF Auth Kit is a modern Django REST Framework authentication toolkit that provides JWT cookies, social login, and multi-factor authentication (MFA) support. It's designed as a reusable Django package with flexible authentication backends.

## Development Commands

### Testing
- Run all tests: `scripts/test_all.sh`
- Run tests with coverage: `scripts/test_all.sh --cov`
- Run specific test environments: `pytest sandbox` or `pytest sandbox_extras/custom_auth`
- Run tests with tox: `tox -e py311` (or py310, py312, py313)

### Code Quality
- Run linter: `scripts/lint.sh`
- Fix linting issues: `scripts/lint.sh --fix`
- Run type checking: `scripts/mypy.sh`
- Run type checking on sandbox: `scripts/mypy.sh --sandbox`
- Run all linting and type checking: `tox -e lint`

### Development Environment
- The project uses UV for dependency management
- Main package code is in `auth_kit/`
- Test environments are in `sandbox/` and `sandbox_extras/`
- Use `sandbox/manage.py` for Django management commands during development

## Architecture

### Core Components

1. **Authentication System** (`auth_kit/authentication.py`):
   - `AuthKitCookieAuthentication`: Cookie-based JWT authentication
   - `AuthKitTokenAuthentication`: Token-based authentication
   - Supports both header and cookie-based token extraction

2. **Settings System** (`auth_kit/app_settings.py`):
   - Dynamic configuration loading using `ImportStr` for lazy imports
   - Centralized settings management with `auth_kit_settings`
   - Configurable serializers, views, and authentication classes

3. **URL Configuration** (`auth_kit/urls.py`):
   - Conditional URL patterns based on `AUTH_TYPE` and `USE_MFA` settings
   - Dynamic inclusion of MFA URLs when enabled
   - JWT-specific endpoints (refresh, verify) when using JWT authentication

4. **Multi-Factor Authentication** (`auth_kit/mfa/`):
   - Modular MFA system with pluggable handlers
   - Support for email-based MFA and other methods
   - Backup codes service for account recovery
   - Dedicated models, serializers, and views for MFA workflows

5. **Social Authentication** (`auth_kit/social/`):
   - Integration with Django Allauth for social login
   - Social account management and connection views
   - Custom templates for social authentication flows

### Key Features

- **Multiple Authentication Types**: JWT (recommended), DRF Token, or custom
- **Cookie Security**: HTTP-only cookies with CSRF protection
- **Flexible Configuration**: Customizable serializers, views, and authentication backends
- **MFA Support**: Optional multi-factor authentication with backup codes
- **Social Login**: Integration with various social providers via Allauth
- **Type Safety**: Full type hints with mypy and pyright support

### Test Structure

The project uses a comprehensive testing approach:

1. **Main Tests** (`sandbox/test_auth_kit/`): Core authentication functionality
2. **MFA Tests** (`sandbox/test_mfa/`): Multi-factor authentication features
3. **Social Tests** (`sandbox/test_social/`): Social authentication flows
4. **Integration Tests** (`sandbox_extras/`): Different authentication configurations
   - `custom_auth/`: Custom authentication backend testing
   - `email_user/`: Email-based user model testing
   - `custom_username/`: Custom username field testing

### Configuration Patterns

The package uses a settings-based configuration system where:
- `AUTH_TYPE` determines the authentication backend ('jwt', 'token', 'custom')
- `USE_AUTH_COOKIE` enables cookie-based authentication
- `USE_MFA` enables multi-factor authentication features
- Dynamic loading of serializers and views based on configuration

### Development Notes

- The project maintains Python 3.10+ compatibility
- Uses modern Django (5.x) and DRF (3.x) versions
- Follows strict type checking with mypy and pyright
- Code formatting with Black and linting with Ruff
- Documentation coverage tracked with interrogate (80% minimum)
- Uses UV for fast dependency resolution and virtual environment management
