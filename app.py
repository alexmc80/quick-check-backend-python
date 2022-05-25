from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/')
def index():
    return "QUICK-CHECK API SERVER FLASK"

# =================== regist/login ===================

@app.route('/register', methods=['POST'])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}

@app.route('/login', methods=['POST'])
def login():
    params = request.json
    user = User.authonticate(**params)
    token = user.get_token()
    return {'access_token': token}
    


# =================== category ===================

@app.route('/categories', methods=['GET'])
@jwt_required()
def select_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter(
        Category.user_id == user_id
        ).all()
    serialaised = []
    for category in categories:
       serialaised.append({
           'id': category.id,
           'name': category.name,
           'description': category.description
       }) 
    return jsonify(serialaised)

@app.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    category = Category(user_id=user_id, **request.json)
    session.add(category)
    session.commit()
    serialaised = {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }    
    return jsonify(serialaised)

@app.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    user_id = get_jwt_identity()
    item = Category.query.filter(
        Category.id == category_id,
        Category.user_id == user_id
        ).first()
    params = request.json    
    if not item:
        return {'message': 'No categories with this id '}, 400
    for key, value in params.items():
        setattr(item, key, value)
    session.commit()
    serialaised = {
            'id': item.id,
            'name': item.name,
            'description': item.description
        }   
    return jsonify(serialaised)

@app.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user_id = get_jwt_identity()
    item = Category.query.filter(
        Category.id == category_id,
        Category.user_id == user_id
        ).first()
    if not item:
        return {'message': 'No categories with this id '}, 400
    session.delete(item)
    session.commit()
    return '', 204

# =================== checklist ===================

# checklists = [
#     {
#         'Id': 1,
#         'Name': 'checklist #1',
#         'Description': 'description #1',
#         'CategoryId': 1,
#         'Status': 0
#     },
#     {
#         'Id': 2,
#         'Name': 'checklist #2',
#         'Description': 'description #2',
#         'CategoryId': 2,
#         'Status': 0
#     }
# ]

# @app.route('/checklists', methods=['GET'])
# def read_checklists():
#     return jsonify(checklists)

# @app.route('/checklists', methods=['POST'])
# def create_checklist():
#     new_on = request.json
#     checklists.append(new_on)
#     return jsonify(checklists)

# @app.route('/checklists/<int:checklist_id>', methods=['PUT'])
# def edit_checklist(checklist_id):
#     item = next((x for x in checklists if x['Id'] == checklist_id), None)
#     params = request.json
#     print(params)
#     if not item:
#         return {'message': 'No checklist with this id '}, 400
#     item.update(params)
#     return item

# @app.route('/checklists/<int:checklist_id>', methods=['DELETE'])
# def delete_checklist(checklist_id):
#     idx, _ = next((x for x in enumerate(checklists)
#                    if x[1]['Id'] == checklist_id), (None, None))
#     checklists.pop(idx)
#     return '', 204


@app.teardown_appcontext
def shutdown_sessionj(exeption=None):
    session.remove()



if __name__ == '__main__':
    app.run(debug=True)
