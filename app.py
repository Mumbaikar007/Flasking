

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required


from security import authenticate, identify


app = Flask ( __name__ )
app.secret_key = 'jose'
api = Api ( app )

jwt = JWT( app, authenticate, identify)

items = []

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument( 'price',
        type=float,
        required=True,
        help="This feild cannot be blank !"
    )

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return { 'item' : item}, 200 if item else 404

    def post(self, name):

        if next(filter(lambda x: x['name'] == name, items), None):
            return { 'message': "An item with name {} already exists".format(name)}, 400

        data = Item.parser.parse_args()
        
        item = {
            'name': name,
            'price': data['price']
        }
        items.append(item)
        return item, 201

    @jwt_required()
    def delete(self, name   ):
        global items
        items = ( filter ( lambda x: x['name'] != name , items), None)
        return { 'message': 'item deleted'}

    @jwt_required
    def put (self, name):
        data = request.get_json()
        item = next(filter( lambda x: x['name'] == name, items), None)

        if item:
            items.update(data)
        else:
            item = {'name' : name, 'price': data['price']}
            items.append(item)

        return item

class ItemList (Resource):
    def get(self):
        return { 'items' : items }


api.add_resource(Item, '/items/<string:name>')
api.add_resource(ItemList, '/items')



app.run( port=5000, debug = True )

