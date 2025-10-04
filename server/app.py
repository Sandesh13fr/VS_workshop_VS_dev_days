import os
import sys
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request, g
from models import init_db, db, Dog, Breed

# Import logging utilities
from utils.logging.config import configure_logging, get_logger
from utils.logging.flask_integration import setup_flask_logging
from utils.logging.examples import log_execution_time

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

# Set up logging
log_config_path = os.path.join(base_dir, 'config', 'logging.json')
log_file_path = os.path.join(base_dir, 'logs', 'app.log')

# Ensure logs directory exists
logs_dir = os.path.join(base_dir, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logging based on environment
is_production = os.environ.get('FLASK_ENV') == 'production'
log_level = "INFO" if is_production else "DEBUG"

# Initialize logging
configure_logging(log_config_path, log_level, log_file_path)

# Create logger for this module
logger = get_logger(__name__)

# Create and configure the Flask application
app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask logging integration
setup_flask_logging(app)

# Initialize the database with the app
logger.info("Initializing database")
try:
    init_db(app)
    logger.info("Database initialization complete")
except Exception as e:
    logger.critical(f"Failed to initialize database: {e}", exc_info=True)
    sys.exit(1)

@app.route('/api/dogs', methods=['GET'])
@log_execution_time
def get_dogs() -> Response:
    logger.info("Fetching all dogs")
    
    # Use contextual logger from request context if available
    ctx_logger = getattr(g, 'logger', logger)
    
    try:
        # Construct the database query
        query = db.session.query(
            Dog.id, 
            Dog.name, 
            Breed.name.label('breed')
        ).join(Breed, Dog.breed_id == Breed.id)
        
        # Add filters based on query parameters
        breed_id = request.args.get('breed_id')
        available_only = request.args.get('available') == 'true'
        
        # Log the filter parameters
        ctx_logger.debug(f"Filter params: breed_id={breed_id}, available_only={available_only}")
        
        if breed_id:
            query = query.filter(Dog.breed_id == breed_id)
            logger.debug(f"Filtering by breed_id: {breed_id}")
        if available_only:
            query = query.filter(Dog.status == 'AVAILABLE')
            logger.debug("Filtering by availability: only available dogs")
        
        # Execute the query
        dogs_query = query.all()
        ctx_logger.debug(f"Found {len(dogs_query)} dogs matching criteria")
        
        # Convert the result to a list of dictionaries
        dogs_list: List[Dict[str, Any]] = [
            {
                'id': dog.id,
                'name': dog.name,
                'breed': dog.breed
            }
            for dog in dogs_query
        ]
        
        logger.info(f"Successfully retrieved {len(dogs_list)} dogs")
        return jsonify(dogs_list)
    
    except Exception as e:
        logger.error(f"Error retrieving dogs: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/dogs/<int:id>', methods=['GET'])
@log_execution_time
def get_dog(id: int) -> tuple[Response, int] | Response:
    logger.info(f"Fetching dog with ID: {id}")
    
    try:
        # Query the specific dog by ID and join with breed to get breed name
        dog_query = db.session.query(
            Dog.id,
            Dog.name,
            Breed.name.label('breed'),
            Dog.age,
            Dog.description,
            Dog.gender,
            Dog.status
        ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()
        
        # Return 404 if dog not found
        if not dog_query:
            logger.warning(f"Dog with ID {id} not found")
            return jsonify({"error": "Dog not found"}), 404
        
        # Convert the result to a dictionary
        dog: Dict[str, Any] = {
            'id': dog_query.id,
            'name': dog_query.name,
            'breed': dog_query.breed,
            'age': dog_query.age,
            'description': dog_query.description,
            'gender': dog_query.gender,
            'status': dog_query.status.name
        }
        
        logger.info(f"Successfully retrieved dog: {dog_query.name} (ID: {id})")
        logger.debug(f"Dog details: {dog}")
        return jsonify(dog)
        
    except Exception as e:
        logger.error(f"Error retrieving dog with ID {id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/breeds', methods=['GET'])
@log_execution_time
def get_breeds() -> Response:
    logger.info("Fetching all dog breeds")
    
    try:
        # Query all breeds
        breeds_query = Breed.query.all()
        
        # Convert the result to a list of dictionaries
        breeds_list: List[Dict[str, Any]] = [
            {
                'id': breed.id,
                'name': breed.name
            }
            for breed in breeds_query
        ]
        
        logger.info(f"Successfully retrieved {len(breeds_list)} breeds")
        logger.debug(f"Breeds: {[breed['name'] for breed in breeds_list]}")
        
        # Document the API response
        return jsonify(breeds_list)
        
    except Exception as e:
        logger.error(f"Error retrieving breeds: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"500 Server Error: {str(error)}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5100))
    
    # Set debug mode based on environment
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # Log application startup
    logger.info(f"Starting Flask server on port {port} (debug={debug_mode})")
    
    # Run the Flask application
    app.run(debug=debug_mode, port=port)  # Port 5100 to avoid macOS conflicts