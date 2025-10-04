package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/go_server/handlers"
	"github.com/go_server/models"
)

// setupRoutes sets up the HTTP routes
func setupRoutes() http.Handler {
	mux := http.NewServeMux()

	// API endpoints
	mux.HandleFunc("/api/dogs", handlers.GetDogsHandler)
	mux.HandleFunc("/api/breeds", handlers.GetBreedsHandler)
	
	// Dog details endpoint with dynamic ID
	mux.HandleFunc("/api/dogs/", func(w http.ResponseWriter, r *http.Request) {
		// Check if the path has the format "/api/dogs/{id}"
		path := r.URL.Path
		if path == "/api/dogs/" {
			http.NotFound(w, r)
			return
		}
		
		handlers.GetDogByIDHandler(w, r)
	})

	return mux
}

func main() {
	// Initialize database connection
	if err := models.InitDB(); err != nil {
		log.Fatalf("Database initialization failed: %v", err)
	}
	
	// Set up routes
	router := setupRoutes()
	
	// Get port from environment variable or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "5100" // Use the same port as the original Flask server
	}
	
	// Start the server
	serverAddr := fmt.Sprintf(":%s", port)
	log.Printf("Server starting on http://localhost%s", serverAddr)
	
	if err := http.ListenAndServe(serverAddr, router); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}