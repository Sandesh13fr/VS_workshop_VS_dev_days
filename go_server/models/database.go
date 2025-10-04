package models

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// DB represents the database connection
var DB *sql.DB

// InitDB initializes the database connection
func InitDB() error {
	// Get the current directory
	dir, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("error getting current directory: %w", err)
	}

	// Use the original SQLite database file path
	dbPath := filepath.Join(dir, "..", "server", "dogshelter.db")
	
	// Open the SQLite database
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return fmt.Errorf("error opening database: %w", err)
	}

	// Set connection parameters
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(time.Hour)

	// Verify the connection
	if err := db.Ping(); err != nil {
		return fmt.Errorf("error connecting to database: %w", err)
	}

	// Set the global DB variable
	DB = db
	log.Printf("Connected to database: %s", dbPath)
	return nil
}

// GetDogs retrieves all dogs from the database, optionally filtered
func GetDogs(breedID *int, availableOnly bool) ([]DogResponse, error) {
	query := `
		SELECT d.id, d.name, b.name as breed
		FROM dogs d
		JOIN breeds b ON d.breed_id = b.id
		WHERE 1=1
	`
	
	// Add filter conditions
	args := []interface{}{}
	if breedID != nil {
		query += " AND d.breed_id = ?"
		args = append(args, *breedID)
	}
	
	if availableOnly {
		query += " AND d.status = ?"
		args = append(args, string(Available))
	}

	// Execute the query
	rows, err := DB.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("error querying dogs: %w", err)
	}
	defer rows.Close()

	// Process results
	var dogs []DogResponse
	for rows.Next() {
		var dog DogResponse
		if err := rows.Scan(&dog.ID, &dog.Name, &dog.Breed); err != nil {
			return nil, fmt.Errorf("error scanning dog row: %w", err)
		}
		dogs = append(dogs, dog)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating dog rows: %w", err)
	}

	return dogs, nil
}

// GetDogByID retrieves a dog by ID
func GetDogByID(id int) (*DogResponse, error) {
	query := `
		SELECT d.id, d.name, b.name as breed, d.age, d.description, d.gender, d.status
		FROM dogs d
		JOIN breeds b ON d.breed_id = b.id
		WHERE d.id = ?
	`
	
	row := DB.QueryRow(query, id)
	
	var dog DogResponse
	var status string
	
	err := row.Scan(
		&dog.ID, 
		&dog.Name, 
		&dog.Breed, 
		&dog.Age, 
		&dog.Description, 
		&dog.Gender, 
		&status,
	)
	
	if err == sql.ErrNoRows {
		return nil, nil
	}
	
	if err != nil {
		return nil, fmt.Errorf("error scanning dog: %w", err)
	}
	
	dog.Status = status
	return &dog, nil
}

// GetBreeds retrieves all breeds from the database
func GetBreeds() ([]BreedResponse, error) {
	query := "SELECT id, name FROM breeds"
	
	rows, err := DB.Query(query)
	if err != nil {
		return nil, fmt.Errorf("error querying breeds: %w", err)
	}
	defer rows.Close()
	
	var breeds []BreedResponse
	for rows.Next() {
		var breed BreedResponse
		if err := rows.Scan(&breed.ID, &breed.Name); err != nil {
			return nil, fmt.Errorf("error scanning breed row: %w", err)
		}
		breeds = append(breeds, breed)
	}
	
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating breed rows: %w", err)
	}
	
	return breeds, nil
}