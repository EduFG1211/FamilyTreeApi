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

# @app.route('/allrelation', methods=['GET'])
# def get_parent():    
#     return jsonify(Parent.getAllParent()), 200

@app.route('/member/<int:id>', methods=['GET'])
def get_member(id):
    person = Person.getSpecificMember(id)
    parents = Person.getAllParent(id)
    sons = Person.getAllSons(id)
    familyTree = {
        "person": person,
        "parents": parents,
        "sons": sons
    }
    return jsonify(familyTree), 200

@app.route('/relation', methods=['POST'])
def handle_parent():
    #----------------------------CREATE POST
    if request.method == 'POST':
        body = request.get_json()
        if body is None:
            return "The request body is null", 400
        if 'person_id' not in body:
            return "You need to specify the person_id", 400
        if 'father_id' not in body:
            return "You need to specify the father_id", 400
        if 'mother_id' not in body:
            return "You need to specify the mother_id", 400       
        
        relation = Parent()
        relation.own_id = body['person_id']
        relation.father_id = body['father_id']
        relation.mother_id = body['mother_id']
        relation.relativity ='person id: '+ str(body['person_id'])+' - '+'father id: '+str(body['father_id'])+' - '+'mother id: '+str(body['mother_id']) 

        verification = Parent.query.filter_by(own_id = body['person_id']).first()
        if verification is None:
            db.session.add(relation)
        elif relation.own_id == verification.own_id:
            return "This user already has a RELATION", 400
        else:
            db.session.add(relation)      
            
        db.session.commit()

        response_body = {"msg": "You POST a RELATION"}        

        return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
