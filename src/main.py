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
from models import db, Person, Parent
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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

@app.route('/all', methods=['GET'])
def get_person():    
    return jsonify(Person.getAllPerson()), 200

@app.route('/allp', methods=['GET'])
def get_parent():    
    return jsonify(Parent.getAllParent()), 200

@app.route('/member/<int:id>', methods=['GET'])
def get_member(id):
    person = Person.getSpecificMember(id)
    parents = Person.getAllParent(id)
    #sons = Person.getAllSons(id)
    familyTree = {
        "person": person,
        "parents": parents,
        #"sons": sons
    }
    return jsonify(familyTree), 200

@app.route('/relation', methods=['POST'])
def handle_parent():
    #----------------------------CREATE POST
    if request.method == 'POST':
        body = request.get_json()
        if body is None:
            return "The request body is null", 400
        if 'name' not in body:
            return "You need to specify the name", 400
        if 'last_name' not in body:
            return "You need to specify the last_name", 400
        if 'age' not in body:
            return "You need to specify the age", 400
        if 'person_id' not in body:
            return "You need to specify the person_id", 400
        if 'type' not in body:
            return "You need to specify the type", 400
        
        person = Person()
        relative1 = Parent()
        relative2 = Parent()

        if body['type'] == 'father':
            relative1.relativity = 'Father'
            response_body = {"msg": "You POST a FATHER"}
        elif body['type'] == 'mother':
            relative1.relativity = 'Mother'
            response_body = {"msg": "You POST a MOTHER"}
        else:
            return "You need to specify a correct type", 400
        
        person.name = body['name']
        person.last_name = body['last_name']
        person.age = body['age']

        db.session.add(person)
        db.session.commit()
        
        relative1.name = body['name']
        relative1.last_name = body['last_name']
        relative1.son_id = body['person_id']

        fromPerson = Person.query.filter_by(id = body['person_id']).first()
        relative2.relativity = 'Son/Daughter'
        relative2.name = fromPerson.name
        relative2.last_name = fromPerson.last_name
        relative2.own_id = fromPerson.id

        newPerson = Person.query.filter_by(name=body['name'], last_name=body['last_name'], age=body['age']).first()
        if body['type'] == 'father':
            relative2.father_id = newPerson.id
        else:
            relative2.mother_id = newPerson.id
        
        relative1.own_id = newPerson.id
        
        db.session.add(relative1)
        db.session.add(relative2)
        db.session.commit()        

        return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
