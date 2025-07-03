# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plugsbox is a NetBox plugin for managing campus network outlets ("prises réseau"). It's a Django-based plugin that extends NetBox functionality to inventory and manage network wall outlets, their connections to switches, patch panels, and associated devices.

## Development Environment

The project uses Docker and Docker Compose for consistent development environments. All development commands are managed through a Makefile.

### Common Development Commands

```bash
# Build Docker images
make cbuild

# Start development environment (foreground for debugging)
make debug

# Start services in background
make start

# Stop services
make stop

# Create NetBox superuser
make adduser

# Open NetBox shell
make nbshell

# Create Django migrations
make migrations

# Build Python package
make pbuild

# Destroy environment and data (caution!)
make destroy
```

### Environment Configuration

- NetBox version and Python version are configurable in Makefile (NETBOX_VER, PYTHON_VER)
- Development environment runs on http://localhost:8002/
- PostgreSQL database runs in Docker container

## Code Architecture

### Core Models

**Plug Model (`plugsbox/models.py:96-426`)**
- Central model representing network wall outlets
- Complex relationships with NetBox core models (Device, Interface, Site, etc.)
- Automatic cable and patch panel management through Django signals
- Status workflow: TO_PATCH → TO_CONFIGURE → OPERATIONAL

**Gestionnaire Model (`plugsbox/models.py:428-524`)**
- Manages plug ownership and permissions
- Auto-creates associated Tenant and UserGroup objects
- Provides user access control integration

### Plugin Structure

```
plugsbox/
├── models.py          # Core data models
├── views.py           # Django views (CRUD operations)
├── forms.py           # Django forms
├── tables.py          # Django-tables2 configurations
├── api/               # REST API endpoints  
├── templates/         # HTML templates
├── static/            # CSS/JS assets
├── migrations/        # Database migrations
└── choices.py         # Status and type choices
```

### Key Integration Points

- **NetBox Core**: Extends Device, Interface, Site, Cable models
- **Automatic Cable Management**: Creates patch panel connections and cables automatically
- **User Permissions**: Integrates with NetBox tenancy and user groups
- **REST API**: Follows NetBox API patterns for external integration

### Plugin Configuration

Plugin registration in `__init__.py` and `config.py`:
- Base URL: `/plugins/plugsbox/`
- Menu integration via `navigation.py`
- Template extensions via `template_content.py`

### Database Design Notes

- Complex foreign key relationships with NetBox core models
- Automatic creation of patch panel devices and ports
- Cable management between wall outlets and switch interfaces
- Support for legacy database ID mapping (`legacy_id` field)

## Testing and Quality

No specific test commands found in current setup. Standard Django testing patterns should apply:
```bash
# Run from within NetBox container
python manage.py test plugsbox
```