from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os

# Set up base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get the base directory of the project
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")  # Use an environment variable for DB URI or default to SQLite

# Initialize Flask application
app = Flask(__name__)  # Create Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE  # Configure the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable the Flask-SQLAlchemy modification tracking feature
app.json.compact = False  # Disable JSON compacting for better readability

# Initialize database and migration tool
db.init_app(app)  # Bind the app with SQLAlchemy
migrate = Migrate(app, db)  # Set up database migration using Flask-Migrate

# Define the home route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'  # Return a simple HTML message as the homepage

# Route to get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    """Fetches all restaurants and returns them as a JSON list."""
    restaurants = Restaurant.query.all()  # Get all restaurants from the database
    restaurants_list = [{"id": r.id, "name": r.name, "address": r.address} for r in restaurants]  # Format the data
    return make_response(jsonify(restaurants_list), 200)  # Return a JSON response with HTTP status 200

# Route to get a specific restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    """Fetches a restaurant by its ID, along with associated pizzas."""
    restaurant = Restaurant.query.get(id)  # Get the restaurant by ID
    if restaurant:
        restaurant_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [{
                "id": rp.id,
                "price": rp.price,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            } for rp in restaurant.restaurant_pizzas]  # Include associated pizzas
        }
        return make_response(jsonify(restaurant_data), 200)  # Return the restaurant data with status 200
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)  # Return 404 if not found

# Route to delete a restaurant by ID
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    with app.app_context():  # Ensure the app context is available
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return jsonify({'message': 'Restaurant deleted successfully'}), 204
        else:
            return jsonify({'error': 'Restaurant not found'}), 404

# Route to get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    """Fetches all pizzas and returns them as a JSON list."""
    pizzas = Pizza.query.all()  # Get all pizzas from the database
    pizzas_list = [{"id": p.id, "name": p.name, "ingredients": p.ingredients} for p in pizzas]  # Format the data
    return make_response(jsonify(pizzas_list), 200)  # Return a JSON response with HTTP status 200

# Route to create a restaurant pizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    """Creates a new restaurant pizza if the price is valid (between 1 and 30)."""
    data = request.get_json()  # Get the JSON payload from the request
    
    # Validate price range (must be between 1 and 30)
    if not (1 <= data.get("price") <= 30):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)  # Return 400 for invalid price
    
    try:
        # Create a new RestaurantPizza instance
        new_restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(new_restaurant_pizza)  # Add the new restaurant pizza to the session
        db.session.commit()  # Commit the session to save the restaurant pizza
        
        # Prepare the response data
        response = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": {
                "id": new_restaurant_pizza.pizza.id,
                "name": new_restaurant_pizza.pizza.name,
                "ingredients": new_restaurant_pizza.pizza.ingredients
            },
            "restaurant": {
                "id": new_restaurant_pizza.restaurant.id,
                "name": new_restaurant_pizza.restaurant.name,
                "address": new_restaurant_pizza.restaurant.address
            }
        }
        return make_response(jsonify(response), 201)  # Return the new restaurant pizza data with status 201
    except Exception as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)  # Return 400 if there was an error

# Run the app on port 5555 with debugging enabled
if __name__ == '__main__':
    app.run(port=5555, debug=True)