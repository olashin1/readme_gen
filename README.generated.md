<div align="center">

# Flask

**A micro web framework for Python designed for simplicity and extensibility.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![License](https://img.shields.io/badge/license-BSD--3--Clause-blue) [![Lock inactive closed issues](https://github.com/pallets/flask/actions/workflows/lock.yaml/badge.svg)](https://github.com/pallets/flask/actions/workflows/lock.yaml) [![GitHub Stars](https://img.shields.io/github/stars/pallets/flask?style=flat)](https://github.com/pallets/flask/stargazers)

[Repository](https://github.com/pallets/flask) • [Website](https://flask.palletsprojects.com) • [Issues](https://github.com/pallets/flask/issues)

</div>

## 🌟 Highlights

- Core utility built on the Werkzeug WSGI toolkit and Jinja2 template engine for reliable request handling and flexible rendering.
- Modular application architecture via Blueprints, allowing developers to organize large codebases into reusable components.
- Integrated development server and a browser-based debugger to streamline the local development and troubleshooting cycle.
- Extensive support for testing with a built-in test client for simulating HTTP requests and a runner for CLI commands.
- Support for asynchronous request handlers and background tasks to handle concurrent operations efficiently.
- Native CLI integration via Click for creating custom administrative commands and managing development workflows.

## ℹ️ Overview

Flask is a lightweight web application framework that provides the essentials for building web services without enforcing a specific project structure or database layer. It is designed to scale from single-file prototypes to complex modular applications, offering a minimal core while remaining highly extensible through a robust ecosystem of third-party integrations.

## ⬇️ Installation

```bash
git clone https://github.com/pallets/flask
cd flask
uv sync
```

## 🚀 Usage

Developers typically initialize a Flask application instance and use decorators to map URL routes to view functions. Interaction with the framework is primarily handled through the 'flask' CLI for running development servers, managing shell contexts, and executing custom scripts. Configuration is managed via Python objects, environment variables, or .env files, and dependencies are typically resolved using tools like uv.

### CLI

```bash
flask
```

## 🛠️ Tech Stack

| Category | Technologies |
| --- | --- |
| **Languages** | Python |
| **Package Management** | uv |

## 🏗️ Architecture

The framework is built as a WSGI application where the central Flask object acts as a registry for routes, configurations, and middleware. It utilizes an internal context system—comprising Application and Request contexts—to manage global state safely across the request lifecycle. The architecture is modular by design, using a 'sans-io' base for core logic and 'Blueprints' to partition application logic into distinct, pluggable units.

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

| | |
| --- | --- |
| **Default branch** | `main` |
| **Topics** | `flask`, `jinja`, `pallets`, `python`, `web-framework`, `werkzeug`, `wsgi` |

## 📄 License

This project is licensed under the **BSD-3-Clause** license.
