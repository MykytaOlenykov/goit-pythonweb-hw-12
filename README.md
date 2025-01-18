# Contacts API

## Description

Contacts API is a RESTful API designed to allow users to create, update, delete, and retrieve their contact lists. Each user can manage their personal contact list, which includes contact details such as names, email addresses, phone numbers, and more. The API is built using FastAPI, PostgreSQL, and Docker for easy deployment and scalability.

---

## Features

- User authentication and authorization (JWT-based).
- CRUD operations for managing contacts.
- Search and filtering for contacts.
- Database-backed storage using PostgreSQL.
- Ready for deployment with Docker and Docker Compose.
- Support for environment-specific configurations using `.env`.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+**
- **Poetry** (for dependency management)
- **Docker** and **Docker Compose**

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MykytaOlenykov/goit-pythonweb-hw-10.git
cd goit-pythonweb-hw-10
```

### 2. Install dependencies:

```bash
poetry install
```

### 3. Set up environment variables

Rename .env.example to .env:

```bash
cp .env.example .env
```

Open the .env file and update it with your local configuration.

### 4. Start the application with Docker

Run the following command to start the API and PostgreSQL database in Docker containers:

```bash
docker-compose up
```

The API will be available at http://localhost:8000

### 5. Access the API

API Documentation: Visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## Environment Variables

| Variable                              | Description                                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------------------------- |
| `POSTGRES_PASSWORD`                   | The password for connecting to the PostgreSQL database.                                     |
| `POSTGRES_USER`                       | The username for connecting to the PostgreSQL database.                                     |
| `POSTGRES_DB`                         | The name of the PostgreSQL database.                                                        |
| `PORT`                                | The port on which the application will run.                                                 |
| `HOST`                                | The host address where the application will be accessible (e.g., `0.0.0.0` or `127.0.0.1`). |
| `BASE_URL`                            | The base URL of the API (e.g., `http://localhost:8000`).                                    |
| `DB_URL`                              | The full database connection URL, including user, password, host, and port.                 |
| `ECHO_SQL`                            | A flag to enable or disable SQL query logging (e.g., `True` or `False`).                    |
| `CORS_ORIGINS`                        | A comma-separated list of allowed origins for Cross-Origin Resource Sharing (CORS).         |
| `JWT_ALGORITHM`                       | The algorithm used for signing JWT tokens (e.g., `HS256`).                                  |
| `JWT_SECRET`                          | The secret key used to sign JWT tokens.                                                     |
| `JWT_VERIFICATION_EXPIRATION_SECONDS` | The expiration time in seconds for JWT token verification.                                  |
| `JWT_ACCESS_EXPIRATION_SECONDS`       | The expiration time in seconds for JWT access tokens.                                       |
| `JWT_REFRESH_EXPIRATION_SECONDS`      | The expiration time in seconds for JWT refresh tokens.                                      |
| `MAIL_USERNAME`                       | The username for the email service.                                                         |
| `MAIL_PASSWORD`                       | The password for the email service.                                                         |
| `MAIL_FROM`                           | The email address from which emails will be sent.                                           |
| `MAIL_SERVER`                         | The SMTP server for sending emails.                                                         |
| `MAIL_FROM_NAME`                      | The display name for the sender of the emails.                                              |
| `MAIL_PORT`                           | The port used to connect to the email service's SMTP server.                                |
| `CLOUDINARY_NAME`                     | The Cloudinary account name for file storage.                                               |
| `CLOUDINARY_API_KEY`                  | The API key for accessing Cloudinary services.                                              |
| `CLOUDINARY_API_SECRET`               | The API secret for accessing Cloudinary services.                                           |

## Additional Information

### Running the api without Docker

If you prefer running the api locally without Docker, follow these steps:

### 1. Install dependencies:

```bash
poetry install
```

### 2. Set up environment variables

Rename .env.example to .env:

```bash
cp .env.example .env
```

Open the .env file and update it with your local configuration.

### 3. Run the application:

```bash
. ./run.sh
```

### 4. Run database migrations:

Ensure PostgreSQL is running locally and the credentials in .env are correct:

```bash
poetry run alembic upgrade head
```
