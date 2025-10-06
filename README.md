# A Backend Server for this [Notes App](https://github.com/njustinbunos/Sticky-Note-Board)

[![My Skills](https://skillicons.dev/icons?i=fastapi,python&theme=dark)](https://skillicons.dev)

A RESTful API for managing sticky notes with customizable colors and position. Built with FastAPI, featuring user authentication using JSON Web Tokens (JWT).

## Features

- Create, read, update, and delete notes
- User authentication with JWT tokens
- Secure password hashing
- User accounts with note ownership
- Set colors for note headers, bodies, and text
- Position notes with X/Y coordinates (0-5000 range)
- data validation for all fields with SQLmodel and Pydantic
- Ready for frontend integration, only local host though

## API Endpoints

### Root Endpoint
- `GET /` - 'Hello World' endpoint

### Authentication

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/register` | Register a new user | `UserCreate` |
| `POST` | `/login` | Login and receive JWT tokens | `LoginRequest` |

### Notes Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/notes/` | Create a new note | `NoteCreate` |
| `GET` | `/notes/` | Get all notes | None |
| `GET` | `/notes/{note_id}` | Get a specific note | None |
| `PUT` | `/notes/{note_id}` | Update a note | `NoteUpdate` |
| `DELETE` | `/notes/{note_id}` | Delete a note | None |

## Data Models

### User Structure

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Login Request

```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

### Login Response (Example)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Note Structure

```json
{
  "id": 1,
  "body": "This is my note content",
  "color_id": "yellow",
  "color_header": "#FFD700",
  "color_body": "#FFFACD",
  "color_text": "#000000",
  "pos_x": 100,
  "pos_y": 150,
  "owner_id": 1
}
```

## Field Specifications

### **User Fields**

| Field | Type | Constraints | Description |
|--------|------|-------------|--------------|
| `id` | integer | primary key, auto-increment | Unique user identifier |
| `username` | string | 3–30 chars, unique, indexed | User’s chosen username |
| `email` | string | valid email (regex), unique, indexed | User’s email address |
| `password_hash` | string | non-null | Hashed password (bcrypt or Argon2) |
| `notes` | relationship | back_populates=`owner` | One-to-many relationship with `Note` |

---

### **Note Fields**

| Field | Type | Constraints | Description |
|--------|------|-------------|--------------|
| `id` | integer | primary key, auto-increment | Unique note identifier |
| `body` | string | 1–500 chars, non-null | Note content |
| `color_id` | string | ≤ 20 chars | Color identifier (e.g., theme name or alias) |
| `color_header` | string | regex: `^#(?:[0-9a-fA-F]{3}){1,2}$` | Header background hex color |
| `color_body` | string | regex: `^#(?:[0-9a-fA-F]{3}){1,2}$` | Body background hex color |
| `color_text` | string | regex: `^#(?:[0-9a-fA-F]{3}){1,2}$` | Text color |
| `pos_x` | integer | 0–5000 (inclusive) | X coordinate position on the board |
| `pos_y` | integer | 0–5000 (inclusive) | Y coordinate position on the board |
| `owner_id` | integer | optional, foreign key → `user.id` | Link to owning user |
| `owner` | relationship | back_populates=`notes` | Many-to-one relationship with `User` |


## Usage Examples

### Registering a User

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Logging In

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

Example Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Creating a Note

```bash
curl -X POST "http://127.0.0.1:8000/notes/" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Remember to buy groceries",
    "color_id": "yellow",
    "color_header": "#FFD700",
    "color_body": "#FFFACD",
    "color_text": "#000000",
    "pos_x": 100,
    "pos_y": 200
  }'
```

### Getting All Notes

```bash
curl -X GET "http://127.0.0.1:8000/notes/"
```

### Updating a Note
```bash
curl -X PUT "http://127.0.0.1:8000/notes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Updated note content",
    "pos_x": 250
  }'
```

### Deleting a Note
```bash
curl -X DELETE "http://127.0.0.1:8000/notes/1"
```

## Database Schema

### Users Table
- `id`: Primary key (auto-generated)
- `username`: Unique username (3-30 chars, indexed)
- `email`: Unique email address (indexed)
- `password_hash`: Hashed password (bcrypt)

### Notes Table
- `id`: Primary key (auto-generated)
- `body`: Note content (1-500 chars)
- `color_id`: Color identifier (max 20 chars)
- `color_header`: Hex color code for header
- `color_body`: Hex color code for body
- `color_text`: Hex color code for text
- `pos_x`: X coordinate (0-5000)
- `pos_y`: Y coordinate (0-5000)
- `owner_id`: Foreign key to users table (optional)

### Relationships
- One user can have many notes (one-to-many)
- Notes can optionally belong to a user

### Database

The application uses SQLite by default. The database file and session management are handled in `database.py`.

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt before storage
- **JWT Authentication**: Secure token-based authentication system
- **Input Validation**: Comprehensive validation on all user inputs
- **Unique Constraints**: Username and email must be unique

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/njustinbunos/Notes-App-API.git
cd Notes-App-API
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
Create a `.env` file for JWT secret keys:
```env
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Quick Start

1. Run the application:
```bash
python main.py runserver
```

2. Open your browser and navigate to:
   - **API Documentation**: http://127.0.0.1:8000/docs
   - **Alternative Docs**: http://127.0.0.1:8000/redoc

## Testing

The application includes unit tests for both notes and authentication functionalities.

### Running Tests

Run all tests:
```bash
python3 main.py test
```

### Test Coverage

- **Authentication Tests**: Registration, login, token validation
- **Notes Tests**: CRUD operations, validations, boundaries, relationships
- **Integration Tests**: Complete user flows and multi-user scenarios

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (duplicate username/email)
- `401`: Unauthorized (invalid credentials)
- `404`: Not found
- `422`: Validation error (invalid input)
- `500`: Server error
