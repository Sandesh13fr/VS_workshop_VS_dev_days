package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go_server/models"
)

// GetDogsHandler handles the GET request to retrieve all dogs
func GetDogsHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse query parameters
	queryParams := r.URL.Query()
	
	// Get breedID parameter if provided
	var breedID *int
	if breedIDStr := queryParams.Get("breed_id"); breedIDStr != "" {
		id, err := strconv.Atoi(breedIDStr)
		if err != nil {
			http.Error(w, "Invalid breed_id parameter", http.StatusBadRequest)
			return
		}
		breedID = &id
	}
	
	// Get available parameter if provided
	availableOnly := queryParams.Get("available") == "true"

	// Get dogs from database
	dogs, err := models.GetDogs(breedID, availableOnly)
	if err != nil {
		http.Error(w, "Error retrieving dogs: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Set content type to JSON
	w.Header().Set("Content-Type", "application/json")
	
	// Write response
	if err := json.NewEncoder(w).Encode(dogs); err != nil {
		http.Error(w, "Error encoding response: "+err.Error(), http.StatusInternalServerError)
		return
	}
}

// GetDogByIDHandler handles the GET request to retrieve a specific dog by ID
func GetDogByIDHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Extract dog ID from URL path
	// Expected format: /api/dogs/{id}
	idStr := r.URL.Path[len("/api/dogs/"):]
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid dog ID", http.StatusBadRequest)
		return
	}

	// Get dog from database
	dog, err := models.GetDogByID(id)
	if err != nil {
		http.Error(w, "Error retrieving dog: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Check if dog exists
	if dog == nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "Dog not found"})
		return
	}

	// Set content type to JSON
	w.Header().Set("Content-Type", "application/json")
	
	// Write response
	if err := json.NewEncoder(w).Encode(dog); err != nil {
		http.Error(w, "Error encoding response: "+err.Error(), http.StatusInternalServerError)
		return
	}
}