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
from models import db, User, People, Planets, FavoritePlanet, FavoritePeople
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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route ('/people') #GET todos los registros people
def get_people():
    all_people = People.query.all()
    all_people_serialized = []
    for person in all_people:
        all_people_serialized.append(person.serialize())
    print(all_people_serialized)
    print(type(all_people))
    return jsonify({'msg': 'get people ok', 'data': all_people_serialized})

@app.route('/users', methods = ['GET'])
def get_users():
    all_users = User.query.all()
    all_users_serialized = []
    for user in all_users: 
        all_users_serialized.append(user.serialize())
    print(all_users_serialized)
    print(type(all_users))
    return jsonify({'msg': 'ok', 'data': all_users_serialized})
    

@app.route ('/planets') #GET todos los registros planets
def get_planets():
    all_planets = Planets.query.all()
    all_planets_serialized = []
    for planet in all_planets:
        all_planets_serialized.append(planet.serialize())
    print(all_planets_serialized)
    print(type(all_planets))
    return jsonify({'msg': 'get people ok', 'data': all_planets_serialized})

@app.route('/planets/<int:planets_id>', methods = ['GET']) #GET info de un planeta por su ID
def get_single_planet(planets_id): 
    planet = Planets.query.get(planets_id)
    #planet.people es un arreglo o lista,  con objetos de la tabla people
    planet_serialized = planet.serialize()
    planet_serialized['people'] = []
    for person in planet.people:
        planet_serialized['people'].append(person.serialize())
    return jsonify({'msg' : f'get single planet with {planets_id} ok', 'data': planet_serialized}) 


@app.route ('/people/<int:people_id>', methods = ['GET']) #GET info de un personaje por su ID
def get_single_person(people_id):
    people = People.query.get(people_id)
    if people is None: 
        return jsonify({'msg': f'personaje with id {people_id} not exist'}), 400
    return jsonify ({'data': people.serialize()})

@app.route('/people', methods = ['POST']) #Adicional, endopoint para crear usuario
def add_people():
    body = request.get_json(silent=True)
    if body is None: 
        return jsonify({'msg': 'Debes enviar informacion en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'debes rellenar el name del personaje'}), 400
    if 'age' not in body: 
        return jsonify({'msg': 'debes rellenar el age del personaje'}), 400
    
    new_person = People()
    new_person.name = body['name']
    new_person.age = body['age']
    db.session.add(new_person)
    db.session.commit()
    print(new_person)
    print(type(new_person))
    return jsonify({'msg': 'new person added'})

@app.route('/user/<int:user_id>/favorites') #GET favoritos de los usuarios 
def get_favorites_by_user(user_id): 
    favorites_planets = FavoritePlanet.query.filter_by(user_id=user_id).all()
    print(favorites_planets)
    favorites_planets_serialized = []
    for favorite in favorites_planets:
        favorites_planets_serialized.append(favorite.planets.serialize())
    
    favorites_people = FavoritePeople.query.filter_by(user_id=user_id).all()
    print(favorites_people)
    favorites_people_serialized = []
    for favorite in favorites_people: 
        favorites_people_serialized.append(favorite.people.serialize())
        return jsonify({
            'msg': f'favoritos del usuario {user_id}:', 
            'favorite_planets': favorites_planets_serialized,
            'favorite_people': favorites_people_serialized})
    return jsonify({'msg': 'ok'})

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)
    new_favorite = FavoritePlanet()
    new_favorite.user_id = user_id
    new_favorite.planets_id = planet_id
    db.session.add(new_favorite)
    db.session.commit()           
    return jsonify({'msg': f'el planeta {planet.name} added in favorites for user {user.id}'})

@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods = ['POST'])
def add_favorite_people(user_id, people_id): 
    user = User.query.get(user_id)
    people = People.query.get(people_id)
    new_favorite = FavoritePeople()
    new_favorite.user_id = user_id
    new_favorite.people_id = people_id
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': f'el personaje {people.name} added in favorites for user {user.id} '})

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite_planet = FavoritePlanet.query.filter_by(user_id=user_id, planets_id=planet_id)
    if favorite_planet is None:
        return jsonify({'msg': 'Favorite planet doesnt exist for this user'}), 400
    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({'msg': 'favorite planet deleted ok'})

@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    favorite_people = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id)
    if favorite_people is None:
        return jsonify({'msg': 'favorite people doesnt exist for this user'}), 400
    db.session.delete(favorite_people)
    db.session.commit()
    return jsonify({'msg': 'favorite people deleted ok'})

 #-------Esto es como contenido extra, no se si estara bien
@app.route('/planet/<int:planet_id>', methods = ['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': 'Planet deleted ok'})

@app.route('/people/<int:people_id>', methods = ['DELETE'])
def delete_people(people_id):
    people = People.query.get(people_id)
    if people is None:
        return jsonify({'msg': 'people not found'}), 404
    db.session.delete(people)
    db.session.commit()
    return jsonify({'msg': 'people deleted ok'})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
