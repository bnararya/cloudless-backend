from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps
import json

app = Flask(__name__)
api = Api(app)

auth_file = open('mongo-credentials.json', 'r')
creds = json.load(auth_file)
app.config['MONGO_URI'] = "mongodb://{user}:{pw}@{host}:{port}/{name}?authSource={authsrc}".format(
    user = creds['MONGO_USERNAME'], pw = creds['MONGO_PASSWORD'], host = creds['MONGO_HOST'], 
    port = creds['MONGO_PORT'], name = creds['MONGO_DBNAME'], authsrc = creds['MONGO_AUTH_SOURCE']
)
auth_file.close()

mongo = PyMongo(app)

class Product(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('identifier', type=int, location='args')
        parser.add_argument('merchant_id', type=str, location='args')
        args = parser.parse_args()
        query = {'identifier':args['identifier'], 'merchant_id':args['merchant_id']}
        product = mongo.db.product.find_one(query)
        return json.loads(dumps(product))

class Merchants(Resource):
    def get(self):
        merchants = mongo.db.merchant.find()
        return json.loads(dumps(merchants))

class Merchant(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('merchant_id', type=str, location='args')
        args = parser.parse_args()
        print(args)
        merchant = mongo.db.merchant.find_one_or_404({'_id': ObjectId(args['merchant_id'])})
        return json.loads(dumps(merchant))

class User(Resource):
    def post(self):
        _json = request.json
        _name = _json['name']
        _email = _json['email']
        _pwd = _json['pwd']
        if _name and _email and _pwd and request.method == 'POST' :
            _hashed_password = generate_password_hash(_pwd)
            _ = mongo.db.user.insert({'name':_name, 'email':_email, 'pwd':_hashed_password})
            resp = jsonify("User added successfully")
            resp.status_code = 200
            return resp
    
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, location='args')
        args = parser.parse_args()
        user = mongo.db.user.find_one_or_404({'_id': ObjectId(args['user_id'])})
        return json.loads(dumps(user))

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, location='args')
        args = parser.parse_args()

        _id = args['user_id']
        _json = request.json
        _name = _json['name']
        _email = _json['email']
        _pwd = _json['pwd']

        if _name and _email and _pwd and _id and request.method == 'PUT':
            _hashed_password = generate_password_hash(_pwd)
            mongo.db.user.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'name': _name, 'email': _email, 'pwd':_hashed_password}})
            resp = jsonify("User update successfully")
            resp.status_code = 200
            return resp

        else :
            return not_found()

    def not_found(error=None):
        message = {
            'status' : 404,
            'message' : 'Not Found' + request.url 
        }
        resp = jsonify(message)
        resp.status_code = 404
        return resp 

class Login(Resource):
    def post(self):
        _json = request.json
        _name = _json['name']
        _pwd = _json['pwd']
        print(_name)
        if _name and _pwd and request.method == 'POST' :
            user = mongo.db.user.find_one_or_404({'name': _name})
            check_password = check_password_hash(user['pwd'], _pwd)
            if check_password:           
                resp = jsonify("Login successfully")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify("Wrong Username or password ")
                resp.status_code = 401
                return resp


api.add_resource(Product, '/product')
api.add_resource(Merchants, '/merchants')
api.add_resource(Merchant, '/merchant')
api.add_resource(User, '/user')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True)