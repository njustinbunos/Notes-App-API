# A Backend Server for this [Notes App](https://github.com/njustinbunos/Sticky-Note-Board)

[![My Skills](https://skillicons.dev/icons?i=fastapi,python&theme=dark)](https://skillicons.dev)

A RESTful API for managing sticky notes with customizable colors and position. Built with FastAPI.

## Features

- Create, read, update, and delete notes
- Set colors for note headers, bodies, and text
- Position notes with X/Y coordinates (0-5000 range)
- User accounts with note ownership
- Comprehensive validation for all fields
- Ready for frontend integration, only local host though.

## API Endpoints

### Root Endpoint
- `GET /` - 'Hello World' endpoint

### Notes Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/notes/` | Create a new note | `NoteCreate` |
| `GET` | `/notes/` | Get all notes | None |
| `GET` | `/notes/{note_id}` | Get a specific note | None |
| `PUT` | `/notes/{note_id}` | Update a note | `NoteUpdate` |
| `DELETE` | `/notes/{note_id}` | Delete a note | None |

## Data Models

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

### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `body` | string | 1-500 chars | Note content |
| `color_id` | string | max 20 chars | Color identifier |
| `color_header` | string | hex color | Header background color |
| `color_body` | string | hex color | Body background color |
| `color_text` | string | hex color | Text color |
| `pos_x` | integer | 0-5000 | X coordinate position |
| `pos_y` | integer | 0-5000 | Y coordinate position |

## Usage Examples

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
- `id`: Primary key
- `username`: Unique username (3-30 chars)
- `email`: Unique email address
- `password_hash`: Hashed password

### Notes Table
- `id`: Primary key
- `body`: Note content (1-500 chars)
- `color_id`: Color identifier (max 20 chars)
- `color_header`: Hex color code for header
- `color_body`: Hex color code for body
- `color_text`: Hex color code for text
- `pos_x`: X coordinate (0-5000)
- `pos_y`: Y coordinate (0-5000)
- `owner_id`: Foreign key to users table

### Database
The application uses SQLite by default. The database file and session management are handled in `database.py`.


## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/njustinbunos/Sticky-Note-Board-API.git
cd Sticky-Notes-Board-API
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

## Quick Start

1. Run the application:
```bash
python main.py
```

2. Open your browser and navigate to:
   - **API Documentation**: http://127.0.0.1:8000/docs
   - **Alternative Docs**: http://127.0.0.1:8000/redoc

