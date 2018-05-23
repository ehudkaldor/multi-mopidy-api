from flask_restful import Resource
from flask import Blueprint, jsonify

# class Clients(Resource):
clients = Blueprint('clients', __name__)

@clients.route("/", methods=['GET'])
def get():
    return jsonify({'message':'clients-get'})

@clients.route("/", methods=['POST'])
def post():
    return jsonify({'message':'clients-post'})
