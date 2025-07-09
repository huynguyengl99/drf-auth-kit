# Contributing to DRF Auth Kit

Thank you for your interest in contributing to DRF Auth Kit! This guide will help you set up the
development environment and understand the tools and processes used in this project.

## Prerequisites

Before starting development, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python package management

## Quick Setup

### Setting up your environment

Create your own virtual environment and activate it:

```bash
uv venv
source .venv/bin/activate
```

Install all development dependencies including extras:
```bash
uv sync --all-extras
```

### Prepare the environment

Before working with the project, ensure:
- Docker is running
- Run `docker compose up` to create necessary databases/services

## Understanding the project structure

The project uses multiple test environments:

1. **Main sandbox** (`sandbox/`): Core testing environment
   - Contains primary test applications and configurations
   - Used for most development and testing
   - Run Django dev server: `python sandbox/manage.py runserver`

2. **Specialized test environments** (`sandbox_extras/`):
   - `custom_auth/`: Tests custom authentication backends
   - `email_user/`: Tests email-based user models
   - `custom_username/`: Tests custom username field configurations
   - These test different user model configurations that require separate Django projects

## Testing

### Running all tests

Use the comprehensive test script that covers all environments:

```bash
# Run all tests across all environments
scripts/test_all.sh

# Run all tests with coverage
scripts/test_all.sh --cov
```

### Running specific test environments

```bash
# Main sandbox tests (most common during development)
pytest --cov=auth_kit --cov-report=term-missing sandbox

# Specific sandbox_extras environment
pytest sandbox_extras/custom_auth
pytest sandbox_extras/email_user
pytest sandbox_extras/custom_username
```

### Using tox for complete environment testing

For testing across multiple Python versions and configurations:

```bash
# Install tox
uv tool install tox

# Run tests on all supported Python versions
tox

# Run tests for specific environment
tox -e py311

# Run only linting checks
tox -e lint
```

## Code quality tools

### Linting and formatting

```bash
# Run linting checks
scripts/lint.sh

# Fix linting issues automatically
scripts/lint.sh --fix
```

This runs:
- [Ruff](https://github.com/astral-sh/ruff) for fast Python linting
- [Black](https://github.com/psf/black) for code formatting
- [toml-sort](https://github.com/pappasam/toml-sort) for TOML file formatting

### Type checking

```bash
# Run mypy on the auth_kit package
scripts/mypy.sh

# Run mypy on the sandbox
scripts/mypy.sh --sandbox

# Run pyright
pyright
```

### Docstring coverage

```bash
# Check docstring coverage (requires 80% minimum)
interrogate -vv auth_kit
```

## Working with the development sandbox

### Setting up and running the sandbox

```bash
# Apply database migrations
python sandbox/manage.py migrate

# Create a superuser
python sandbox/manage.py createsuperuser

# Run Django development server
python sandbox/manage.py runserver
```

Once running, you can:
- Access admin interface at http://127.0.0.1:8000/admin/
- Test API endpoints manually
- Verify package functionality in real Django environment

## Pre-submission checklist

Before creating a pull request, ensure:

### 1. All tests pass
```bash
scripts/test_all.sh --cov
```

### 2. Code quality checks pass
```bash
scripts/lint.sh
scripts/mypy.sh
scripts/mypy.sh --sandbox
pyright
```

### 3. Documentation coverage meets requirements
```bash
interrogate -vv auth_kit
```

### 4. Comprehensive testing with tox
```bash
tox
```

## Commit guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]
```

Examples:
- `feat(auth): add custom authentication backend support`
- `fix(mfa): resolve backup code validation issue`
- `docs(readme): update installation instructions`

## Customization and extensions

DRF Auth Kit is designed for extensibility. When contributing:

- **Custom authentication backends**: Support for different token types and validation methods
- **MFA enhancements**: Additional MFA handlers and verification methods
- **Social authentication**: Integration with new providers or enhanced OAuth flows
- **Serializer customization**: Flexible request/response serializer composition
- **Documentation improvements**: Better guides and examples

For detailed customization patterns, see the [Customization Guide](docs/user-guides/customization.rst).

## Development best practices

- **Keep changes focused**: Each PR should address a single concern
- **Write descriptive docstrings**: All public API functions should be well-documented
- **Add type annotations**: All code should be properly typed
- **Follow Django/DRF conventions**: Use Django and DRF best practices
- **Test thoroughly**: Include tests for all new functionality
- **Consider backwards compatibility**: Ensure package works with multiple Django/DRF versions

## Package-specific considerations

- **Multiple Django versions**: Tested against multiple Django versions (see tox.ini)
- **Django REST Framework compatibility**: Ensure features work with supported DRF versions
- **Installation and distribution**: Test that the package installs correctly via pip
- **Documentation**: Update documentation for any API changes

Thank you for contributing to DRF Auth Kit!
