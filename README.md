# Banking-project ™️

## Technologies Used on the Platform 💻

- Flask 
- PostgreSQL
- Flask-SQLAlchemy
- Flask Alembic

## Project Architecture

### Modular Architecture

This project uses a modular architecture, organized within a monolith. Modularization facilitates maintenance, scalability, and code comprehension, allowing different parts of the application to be developed and managed separately.

### Directory Structure

The project's directory structure is organized as follows:

```
docs/
LICENSE
local.py
README.md
requirements.txt
src/
    auth/
    config.py
    __init__.py
    models/
    __pycache__/
    static/
    templates/
    utils/
    routes/
    wsgi.py
test/
```

### Directory and File Descriptions

- **docs/**: Contains the project's documentation.
- **instance/**: Stores instance-specific configuration files that are not versioned.
- **LICENSE**: Information about the project's licensing.
- **local.py**: Local configuration file, used for environment-specific settings during development.
- **migrations/**: Directory containing database migrations, typically managed with `Flask-Migrate` and `Alembic`.
- **proposta/**: Directory that may contain specifications or proposal documents for the project.
- **README.md**: Provides an overview of the project, including installation and usage instructions.
- **requirements.txt**: List of Python dependencies required for the project.
- **src/**: Main directory for the application's source code.
  - **auth/**: Module responsible for authentication, containing blueprints, forms, and related logic.
  - **config.py**: Configuration file defining different environments (development, production, etc.).
  - **__init__.py**: Contains the factory function to create and configure the Flask instance.
  - **models/**: Module containing the database model definitions.
  - **__pycache__/**: Automatically generated directory by Python for storing compiled bytecode files.
  - **static/**: Directory for static files such as CSS, JavaScript, and images.
  - **templates/**: Directory for HTML templates to be rendered by views.
  - **utils/**: Module with utility functions and helpers used across different parts of the application.
  - **routes/**: Module containing the application's views where routes are defined.
  - **wsgi.py**: Entry point for WSGI servers, used to deploy the application.
- **test/**: Directory for unit and integration tests.



### Factory Pattern

The project follows the factory pattern to create and configure the Flask instance, which allows for greater flexibility and ease of testing. An example of a factory function can be found in the `src/__init__.py` file:

```python
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config')

    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    # More initializations and registrations...

    return app
```

### Benefits of Modular Architecture

- **Maintainability**: Code organized in modules facilitates maintenance and updates.
- **Scalability**: Allows different modules to be scaled independently as needed.
- **Comprehension**: Clear and well-defined structure makes it easier for new developers to understand the project.
- **Reusability**: Modules can be reused in different parts of the application or in other projects.

---