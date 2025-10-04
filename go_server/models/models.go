package models

import (
	"time"
)

// AdoptionStatus represents the current adoption status of a dog
type AdoptionStatus string

const (
	Available AdoptionStatus = "AVAILABLE"
	Adopted   AdoptionStatus = "ADOPTED"
	Pending   AdoptionStatus = "PENDING"
)

// Dog represents a dog in the shelter
type Dog struct {
	ID           int           `json:"id"`
	Name         string        `json:"name"`
	BreedID      int           `json:"breed_id"`
	Age          int           `json:"age"`
	Gender       string        `json:"gender"`
	Description  string        `json:"description"`
	Status       AdoptionStatus `json:"status"`
	IntakeDate   time.Time     `json:"-"`
	AdoptionDate *time.Time    `json:"-"`
}

// Breed represents a dog breed
type Breed struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
}

// DogResponse is the structure for dog API responses
type DogResponse struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Breed       string `json:"breed"`
	Age         int    `json:"age,omitempty"`
	Gender      string `json:"gender,omitempty"`
	Description string `json:"description,omitempty"`
	Status      string `json:"status,omitempty"`
}

// BreedResponse is the structure for breed API responses
type BreedResponse struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// ErrorResponse is used for error messages
type ErrorResponse struct {
	Error string `json:"error"`
}

// Validate validates a dog's data
func (d *Dog) Validate() bool {
	if d.Name == "" || len(d.Name) < 2 {
		return false
	}

	// Gender validation
	if d.Gender != "Male" && d.Gender != "Female" && d.Gender != "Unknown" {
		return false
	}

	// Description validation - if provided, must be at least 10 chars
	if d.Description != "" && len(d.Description) < 10 {
		return false
	}

	return true
}

// Validate validates a breed's data
func (b *Breed) Validate() bool {
	if b.Name == "" || len(b.Name) < 2 {
		return false
	}

	// Description validation - if provided, must be at least 10 chars
	if b.Description != "" && len(b.Description) < 10 {
		return false
	}

	return true
}