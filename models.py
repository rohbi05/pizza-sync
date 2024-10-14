from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin

# Define naming convention for foreign keys to ensure database consistency
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)

# Restaurant model representing a restaurant entity in the database
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    # Define primary key column 'id'
    id = db.Column(db.Integer, primary_key=True)

    # Define 'name' and 'address' columns for the restaurant
    name = db.Column(db.String)
    address = db.Column(db.String)

    # One-to-many relationship with RestaurantPizza (a restaurant can have multiple pizzas)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza',
        backref='restaurant',
        lazy=True,
        cascade="all, delete-orphan"  # Enable cascading delete
    )

    # Specify serialization rules to avoid circular references when serializing data
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        # String representation for Restaurant, useful for debugging
        return f'<Restaurant {self.name}>'

# Pizza model representing a pizza entity in the database
class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    # Define primary key column 'id'
    id = db.Column(db.Integer, primary_key=True)

    # Define 'name' and 'ingredients' columns for the pizza
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # One-to-many relationship with RestaurantPizza (a pizza can be available in multiple restaurants)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', lazy=True)

    # Specify serialization rules to avoid circular references when serializing data
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        # String representation for Pizza, useful for debugging
        return f'<Pizza {self.name}, {self.ingredients}>'

# RestaurantPizza model representing the association between restaurants and pizzas
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    # Define primary key column 'id'
    id = db.Column(db.Integer, primary_key=True)

    # Define 'price' column with validation to ensure it's between 1 and 30
    price = db.Column(db.Integer, nullable=False)

    # Foreign key column 'pizza_id', referencing the 'pizzas' table
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    # Foreign key column 'restaurant_id', referencing the 'restaurants' table
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Validator method to ensure the price is between 1 and 30
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            # Raise an exception if the price is not within the valid range
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        # String representation for RestaurantPizza, useful for debugging
        return f'<RestaurantPizza ${self.price}>'
