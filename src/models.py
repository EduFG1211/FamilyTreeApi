from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

db = SQLAlchemy()

class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    son_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    mother_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    own_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    relativity = db.Column(db.String(250), nullable=False)

    def getAllParent():
        list_parent = Parent.query.all()
        list_parent = list(map(lambda x: x.serialize(), list_parent))
        return(list_parent) 

    def serialize(self):
        return {
            "id": self.id,
            "father_id": self.father_id,
            "mother_id": self.mother_id,
            "son_id": self.son_id,
            "own_id": self.own_id,
            "name": self.name,
            "last_name": self.last_name,
            "relativity": self.relativity,            
        }

class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def getAllPerson():
        list_person = Person.query.all()
        list_person = list(map(lambda x: x.serialize(), list_person))
        list_person.sort(key=lambda x: x["age"], reverse=True) 
        return(list_person)

    def getSpecificMember(id):
        member = Person.query.filter_by(id=id).first()
        person = {
            "name": member.name,
            "last_name": member.last_name,
            "age": member.age,
        }
        return person

    # def getAllParent(id):
    #     member = Parent.query.filter_by(son_id=id).first()
    #     if member is None:
    #         return "No tiene padres"
    #     father = Person.getSpecificMember(member.father_id)
    #     mother = Person.getSpecificMember(member.mother_id)
    #     response = {
    #         "father": father,
    #         #"mother": mother
    #     }
    #     return response

    def getAllParent(id):
        member1 = Parent.query.filter_by(son_id=id, relativity = 'Father').first()
        member2 = Parent.query.filter_by(son_id=id, relativity = 'Mother').first()
        if member1 is None and member2 is None:
            return "There are no info of the parents"
        elif member1 is None:
            mother = Person.getSpecificMember(member2.own_id)
            response = {"father":"None", "mother": mother}
        elif member2 is None:
            father = Person.getSpecificMember(member1.own_id)
            response = {"father": father, "mother": "None"}
        else:
            father = Person.getSpecificMember(member1.own_id)
            mother = Person.getSpecificMember(member2.own_id)
            response = {"father": father, "mother": mother}
        return response

    # def getAllSons(id):
    #     member_list = Parent.query.filter(or_(Parent.father_id==id, Parent.mother_id==id))
    #     if member_list is None:
    #         return "No tiene hijos"
    #     member_list = list(map(lambda x: Person.getSpecificMember(x.son_id), member_list))
    #     if len(member_list) == 0:
    #         return "No tiene hijos"
    #     response = {
    #         "sons": member_list
    #     }
    #     return response

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "age": self.age,
        }