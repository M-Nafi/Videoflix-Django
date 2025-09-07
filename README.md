# Videoflix Backend

A Django REST Framework backend for a video streaming service similar to Netflix. This application allows users to register, log in, and stream videos in various resolutions.

## Technologies

-   **Python/Django**: Backend framework
-   **Django REST Framework**: API development
-   **PostgreSQL**: Primary database
-   **Redis**: Caching and background jobs
-   **Django RQ**: Background task processing
-   **Docker**: Containerization
-   **JWT**: Authentication
-   **FFmpeg**: Video transcoding (HLS streaming)

## Prerequisites

-   Docker Desktop
-   Git

## Installation

1. Clone the repository:

    ```bash
    git clone [repository-url]
    cd videoflix-django-app
    ```

2. Create a `.env` file based on the `.env.template`:

    ```bash
    cp .env.template .env
    ```

3. Adjust the environment variables in the `.env` file:

    ```bash
    DB_NAME=videoflix
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432
    DJANGO_SUPERUSER_USERNAME=admin
    DJANGO_SUPERUSER_EMAIL=admin@example.com
    DJANGO_SUPERUSER_PASSWORD=adminpassword
    ```

4. Start the Docker containers:

    ```bash
    docker-compose up --build
    ```

5. The backend will be available at:

    ```
    http://localhost:8000
    ```

## Running Tests

You can execute tests directly within the running Docker container:

```bash
# Run all tests
docker compose exec web pytest

# Run tests with coverage report
docker compose exec web coverage run -m pytest
docker compose exec web coverage report
```

To generate a detailed HTML coverage report:

```bash
docker compose exec web coverage html
```

The report will be created inside the container under the `htmlcov/` directory.

## API Documentation

The API provides the following main endpoints:

### User Authentication

-   `/api/register/`: User registration
-   `/api/activate/<uidb64>/<token>/`: Account activation
-   `/api/login/`: User login (JWT token)
-   `/api/logout/`: User logout
-   `/api/token/refresh/`: Refresh JWT token
-   `/api/password_reset/`: Request password reset
-   `/api/password_confirm/<uidb64>/<token>/`: Confirm password reset

### Video Streaming

-   `/api/video/`: List all available videos
-   `/api/video/<int:movie_id>/<str:resolution>/index.m3u8`: HLS manifest for a video
-   `/api/video/<int:movie_id>/<str:resolution>/<str:segment>/`: Video segment

A complete API documentation is available at `/api/`.

## Key Features

-   Email-activated user registration
-   JWT-based authentication
-   Adaptive video streaming (HLS)
-   Support for multiple video resolutions (480p, 720p, 1080p)
-   Background processing for video transcoding
-   Redis caching for enhanced performance

## Project Structure

The project follows a standard Django layout with separate apps for different responsibilities:

-   `user_auth_app`: User authentication and management
-   `content`: Video management and streaming
-   `core`: Project settings and configuration

## Development

For local development:

1. The Docker container is configured for auto-reloading on code changes.
2. Modify the code in your local development environment.
3. Changes are automatically reflected in the running container.

## Note

This project is intended for educational purposes and serves as an example implementation of a Django and DRF-based video streaming service.
