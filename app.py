from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

products = {
    0 : {"name": "Aqua","price": 3000},
    1 : {"name": "Indomie","price": 3000},
    2 : {"name": "Oreo","price": 3000},
    3 : {"name": "Ultra Milk","price": 3000}
}

class Product(Resource):
    def get(self, product_id):
        return products[product_id]

api.add_resource(Product, '/product/<int:product_id>')

if __name__ == '__main__':
    app.run(debug=False)