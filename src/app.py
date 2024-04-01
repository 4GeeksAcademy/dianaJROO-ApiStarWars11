"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, FavoritePeople, FavoritePlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():

     users = User.query.all() # SELECT * from users;

     return jsonify([ person.serialize() for person in users ]), 200


@app.route('/people', methods=['GET'])
def get_people():

    peoples = People.query.all()
    return jsonify([people.serialize() for people in peoples]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):

    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize())
    else:
        return jsonify({"error": "Person not found"}), 404    

@app.route('/planets', methods=['GET'])
def get_planet():

    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planeta(planet_id):
    
    planeta = Planet.query.get(planet_id)
    if planeta:
        return jsonify(planeta.serialize())
    else:
        return jsonify({"error": "Planet not found"}), 404

@app.route('/users/favorites', methods=['GET'])
def favorite_people():

     favorite_people = FavoritePeople.query.all() # SELECT * from users;
     favorite_planet = FavoritePlanet.query.all()
     result1 = list(map(lambda item: item.serialize(), favorite_people))
     result2 = list(map(lambda item: item.serialize(), favorite_planet))

     return jsonify(result1, result2), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

  user = User.query.first()

  if user: 
    planeta = Planet.query.get(planet_id)
    if planeta: 
        favorite_planet = FavoritePlanet( user_id = user.id, planet_id = planet_id )
        db.session.add(favorite_planet)
        db.session.commit()
        return jsonify({'msg': 'Planeta agregado'}), 200
    return jsonify({'msg': 'Planeta not Found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):

  user = User.query.first()

  if user: 
    personas = People.query.get(people_id)
    if personas: 
        favorite_people = FavoritePeople( user_id = user.id, people_id = people_id )
        db.session.add(favorite_people)
        db.session.commit()
        return jsonify({'msg': 'People agregado'}), 200
    return jsonify({'msg': 'People not Found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    favorite_people= FavoritePeople.query.get(people_id)
    db.session.delete(favorite_people)
    db.session.commit()

    return jsonify({'msg': 'People Delete'}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    favorite_planet= FavoritePlanet.query.get(planet_id)
    db.session.delete(favorite_planet)
    db.session.commit()

    return jsonify({'msg': 'Planet Delete'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
