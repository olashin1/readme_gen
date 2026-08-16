<div align="center">

# Flask

**A simple framework for building complex web applications.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![License](https://img.shields.io/badge/license-BSD--3--Clause-blue) [![Lock inactive closed issues](https://github.com/pallets/flask/actions/workflows/lock.yaml/badge.svg)](https://github.com/pallets/flask/actions/workflows/lock.yaml) [![GitHub Stars](https://img.shields.io/github/stars/pallets/flask?style=flat)](https://github.com/pallets/flask/stargazers)

[Repository](https://github.com/pallets/flask) • [Website](https://flask.palletsprojects.com) • [Issues](https://github.com/pallets/flask/issues)

</div>

## ✨ Overview

Flask is a lightweight Python web framework built on the Werkzeug WSGI toolkit and Jinja2 template engine, designed for developing web applications and APIs.

## 🚀 Features

- WSGI-compliant application object for handling web requests.
- Integrated routing system based on Werkzeug with support for URL variables and converters.
- Templating engine integration using Jinja2 with template inheritance support.
- Blueprint system for modular application design and route organization.
- Application and request context management using context locals (g, request, session, current_app).
- Extensible configuration system supporting object, file, and environment-based settings.
- CLI integration via Click for application management and custom command registration.
- Support for asynchronous route handlers and error handlers via asgiref.
- Built-in session management using secure cookie-based signed headers.
- Signals support via the Blinker library for application lifecycle hooks.
- Comprehensive testing suite utilities including FlaskClient and FlaskCliRunner.

## ⚡ Quick Start

### Installation

```bash
git clone https://github.com/pallets/flask
cd flask
uv sync
```

### Usage

Applications are initialized via the Flask class and routes are defined using decorators such as @app.route(). Deployment is managed through the 'flask' CLI, which uses environment variables like FLASK_APP to locate the application. It supports development servers via 'flask run' and production deployment through WSGI containers like Gunicorn or Waitress.

```bash
flask
```

## 🛠️ Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **Package Management** | uv           |

## 🏗️ Architecture

The framework uses a layered architecture where the core 'Flask' object inherits from a 'Scaffold' base class. It relies on Werkzeug for HTTP abstractions and routing, Jinja2 for templating, and ItsDangerous for secure data signing. Logic is partially organized into 'sans-io' components to separate core application logic from the WSGI interface.

## 📁 Project Structure

```text
flask/
├── src/  # Source code
│   └── flask/
├── tests/  # Test suite
├── docs/  # Documentation
├── examples/  # Examples
├── .github/  # GitHub configuration
│   └── workflows/  # CI/CD workflows
├── pyproject.toml  # Python project configuration
├── LICENSE.txt  # License
└── README.md  # Project documentation
```

## 🔗 Repository

|                    |                                                                            |
| ------------------ | -------------------------------------------------------------------------- |
| **Default branch** | `main`                                                                     |
| **Topics**         | `flask`, `jinja`, `pallets`, `python`, `web-framework`, `werkzeug`, `wsgi` |

## 📄 License

This project is licensed under the **BSD-3-Clause** license.
