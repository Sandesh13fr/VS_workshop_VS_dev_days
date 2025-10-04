# Go Server Implementation for Dog Shelter API

This is a Go-based implementation of the original Python Flask server for the dog shelter application. It provides identical API endpoints and functionality.

## Prerequisites

1. Go (version 1.17 or higher)
2. SQLite3

## Installation

1. Clone the repository
2. Navigate to the `go_server` directory
3. Install dependencies:
   ```
   go mod tidy
   ```

## Running the Server

From the `go_server` directory, run:

```
go run main.go
```

This will start the server at http://localhost:5100

## API Endpoints

### 1. Get all dogs

```
GET /api/dogs
```

Query parameters:
- `breed_id`: Filter dogs by breed ID
- `available`: When set to `true`, return only available dogs

Example response:
```json
[
  {
    "id": 1,
    "name": "Buddy",
    "breed": "Labrador Retriever"
  },
  {
    "id": 2,
    "name": "Max",
    "breed": "German Shepherd"
  }
]
```

### 2. Get a specific dog

```
GET /api/dogs/{id}
```

Example response:
```json
{
  "id": 1,
  "name": "Buddy",
  "breed": "Labrador Retriever",
  "age": 3,
  "description": "Friendly and playful",
  "gender": "Male",
  "status": "AVAILABLE"
}
```

### 3. Get all breeds

```
GET /api/breeds
```

Example response:
```json
[
  {
    "id": 1,
    "name": "Labrador Retriever"
  },
  {
    "id": 2,
    "name": "German Shepherd"
  }
]
```

## Project Structure

- `main.go`: Server initialization and configuration
- `handlers/`: API endpoint handlers
  - `dogs.go`: Handlers for dog-related endpoints
  - `breeds.go`: Handlers for breed-related endpoints
- `models/`: Data models and database operations
  - `models.go`: Data structures
  - `database.go`: Database operations
- `utils/`: Utility functions

## Implementation Details

1. **Database Connection**: The server connects to the existing SQLite database file.
2. **API Compatibility**: All endpoints match the original Flask implementation.
3. **Error Handling**: The server includes proper error handling and status codes.
4. **Minimal Dependencies**: Uses only the standard library and SQLite driver.

## Differences from Flask Implementation

1. **Routing**: Go's `http.ServeMux` is used instead of Flask's decorators.
2. **Database Access**: Uses Go's `database/sql` package instead of SQLAlchemy ORM.
3. **Middleware**: Custom middleware for logging instead of Flask's built-in features.