<div align="center">

# yewentai-TODO-APP-899635c

**A full-stack task management application built with FastAPI and React.**

![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=white) ![pip](https://img.shields.io/badge/pip-3775A9?logo=pypi&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Vitest](https://img.shields.io/badge/Vitest-6E9F18?logo=vitest&logoColor=white)

[Repository](https://github.com/yewentai/TODO-APP) • [Issues](https://github.com/yewentai/TODO-APP/issues)

</div>

## Highlights

- Task lifecycle management including creation, status toggling, and deletion.
- Automated task statistics calculation for total, completed, and pending items.
- Responsive web interface styled with utility-first CSS.
- RESTful API with endpoints for task manipulation and health monitoring.
- Containerized environment configuration for both client and server components.
- Client-side state management with custom hooks and asynchronous API integration.

## Overview

This project provides a functional task management system for organizing daily objectives through a web-based interface. It enables users to create, view, update, and remove tasks while tracking progress with built-in metrics. The application integrates a Python-based backend with a JavaScript frontend to deliver a responsive experience for personal productivity management.

## Tech Stack

| Category | Technologies |
| --- | --- |
| **Languages** | JavaScript, Python |
| **Backend** | FastAPI |
| **Build System** | Vite |
| **Deployment** | Docker |
| **Frontend** | React |
| **HTTP client** | Axios |
| **Styling** | Tailwind CSS |
| **Testing** | Vitest |
| **Package Management** | pip, npm |

## Installation

```bash
git clone https://github.com/yewentai/TODO-APP
cd TODO-APP
python -m pip install -r backend/requirements.txt
npm --prefix frontend install
```

## Building

```bash
npm --prefix frontend run build
```

## Usage

The application is divided into a backend and a frontend service. The backend is started using Uvicorn to serve the FastAPI application, while the frontend is launched via Vite for local development. Users manage tasks through the browser interface, which communicates with the API to persist changes. Dockerfiles are included to build images for both components.

### Project Commands

| Purpose | Command |
| --- | --- |
| Dev | `npm --prefix frontend run dev` |
| Preview | `npm --prefix frontend run preview` |
| Api | `python -m uvicorn backend.main:app --reload` |

## Examples

### Example 1

```text
---

## ⚙️ Prerequisites

* **Node.js** ≥ 16.0.0 & **npm** ≥ 7.0.0
* **Python** ≥ 3.8 & **pip**
* (Optional) **Virtual Environment** - Recommended for Python dependencies
* (Optional) **WSL2** or Unix-like shell for development

---

## 🚀 Quick Start

### 1. Clone & Setup
```

### Example 2

```text
### 2. Backend Setup
```

### Example 3

```text
**Backend will be running at:**

* **API:** <http://localhost:8000>
* **Interactive Docs:** <http://localhost:8000/docs>
* **Alternative Docs:** <http://localhost:8000/redoc>

### 3. Frontend Setup
```

## API Endpoints

| Method | Path | Handler |
| --- | --- | --- |
| `GET` | `/` | `root` |
| `GET` | `/tasks` | `get_tasks` |
| `POST` | `/tasks` | `create_task` |
| `GET` | `/tasks/stats` | `get_task_stats` |
| `DELETE` | `/tasks/{task_id}` | `delete_task` |
| `GET` | `/tasks/{task_id}` | `get_task` |
| `PUT` | `/tasks/{task_id}` | `update_task` |

## Environment Variables

The application reads the following variable names. Values are not included in this README.

| Variable | Detected in |
| --- | --- |
| `VITE_API_URL` | `frontend/.env`, `frontend/src/services/taskService.js` |

## Testing

```bash
npm --prefix frontend run lint
npm --prefix frontend run test
```

## Architecture

The project employs a decoupled architecture consisting of a Python backend and a React frontend. The backend uses FastAPI to provide a REST API with Pydantic for data validation and basic in-memory storage. The frontend uses React with Tailwind CSS for styling and Axios for HTTP communication. Both services are designed to be independent, communicating over network protocols with CORS configuration.

## Project Structure

```text
TODO-APP/
├── backend/
├── frontend/
│   ├── public/
│   └── src/
└── README.md  # Project documentation
```

## Repository

| | |
| --- | --- |
| **Default branch** | `main` |
