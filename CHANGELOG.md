## v0.2.6 (2025-07-12)

### Fix

- **social**: update type hint for social_urls

## v0.2.5 (2025-07-12)

### Fix

- **social**: handle database unavailability during URL generation

## v0.2.4 (2025-07-12)

### Fix

- **serializers**: add _has_phone_field property to RegisterSerializer

## v0.2.3 (2025-07-12)

### Fix

- **dependencies**: loosen version for drf spectacular and structlog

## v0.2.2 (2025-07-09)

### Fix

- **roadmap**: add upcoming features documentation and roadmap
- **contributing**: update development workflow and testing practices

## v0.2.1 (2025-07-09)

### Fix

- **rtd**: install all extras for building readthedocs

## v0.2.0 (2025-07-09)

### Feat

- **auth**: enhance registration, user validation, and error handling
- **i18n**: add internationalization support with 50+ language locales
- **urls**: add URL exclusion functionality via EXCLUDED_URL_NAMES setting
- **auth**: add login redirect support with next and redirect_to parameters
- **mfa**: improved internationalization support and type safety
- **mfa**: add i18n support and comprehensive API documentation
- **mfa**: add multi-factor authentication support
- **social**: add comprehensive social authentication support with django-allauth integration
- **tests**: add comprehensive test suite and sandbox examples
- **serializers**: add dynamic serializer loading and improved authentication

### Fix

- **api**: correct registration descriptions and add missing i18n for social auth
- **package**: update package dependencies
- **rtd**: ignore building docs if the commit message is not bump version
- **coverage**: export xml for cov report

## v0.1.1 (2025-06-19)

### Fix

- **pyproject**: rename package from auth_kit to drf-auth-kit

## v0.1.0 (2025-06-19)

### Feat

- **auth**: implement complete DRF authentication kit with JWT, token, and custom auth support
- **setup**: initialize project
