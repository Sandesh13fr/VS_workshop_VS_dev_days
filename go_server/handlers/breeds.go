package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/go_server/models"
)

// GetBreedsHandler handles the GET request to retrieve all breeds
func GetBreedsHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow GET requests
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Get breeds from database
	breeds, err := models.GetBreeds()
	if err != nil {
		http.Error(w, "Error retrieving breeds: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Set content type to JSON
	w.Header().Set("Content-Type", "application/json")
	
	// Write response
	if err := json.NewEncoder(w).Encode(breeds); err != nil {
		http.Error(w, "Error encoding response: "+err.Error(), http.StatusInternalServerError)
		return
	}
}