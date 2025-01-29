from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    fav_planet = db.relationship('FavoritePlanet', back_populates= 'user')
    fav_people = db.relationship('FavoritePeople', back_populates = 'user')

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class People(db.Model):
    __tablename__ = 'people' 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique=True, nullable = False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planets = db.relationship('Planets', back_populates = 'people')
    fav_people = db.relationship('FavoritePeople', back_populates = 'people')

    def __repr__(self):
        return f'El personaje {self.id} con nombre {self.name}'
    
    def serialize(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "age": self.age
        }
    
class Planets(db.Model): 
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique=True, nullable=False)
    color = db.Column(db.String)
    people = db.relationship('People', back_populates = 'planets')
    fav_planet = db.relationship('FavoritePlanet', back_populates= 'planets')
    
    def __repr__(self):
        return f'El planeta {self.id} con nombre {self.name}'
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'color': self.color
        }

class FavoritePlanet (db.Model): 
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates = 'fav_planet')
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planets = db.relationship('Planets', back_populates = 'fav_planet')

    def __repr__(self): 
        return f'Al usuario {self.user_id} le gusta el planeta {self.planets_id}'
    def serialize(self):
        return{
            'id': self.id,
            'user_id': self.user_id, 
            'planets_id': self.planets_id
        }

class FavoritePeople (db.Model):
    __tablename__ = 'favorite_people'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates = 'fav_people')
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    people = db.relationship('People', back_populates = 'fav_people')

    def __repr__(self): 
        return f'Al usuario {self.user_id} le gusta el personaje {self.people_id}'

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id, 
            'people_id': self.people_id
        }