import os
import re
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

# ROUTES


# get drinks in a short representation
@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_reps = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_reps
        })
    except:
        abort(404)


# get drinks in a long representaion with an authorization
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        drinks_rep = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_rep
        })
    except:
        abort(404)


# post new drink with an authorization
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    body = request.get_json()
    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        drink_rep = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': drink_rep
        })

    except:
        abort(400)


# update a drink with a specific id, have an authorization
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    body = request.get_json()
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    try:
        drink = Drink.query.get_or_404(id)
        if new_title:
            drink.title = new_title
        if new_recipe:
            drink.recipe = json.dumps(new_recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(400)


# delete a drink with specific id, have authorization
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.get_or_404(id)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })

    except:
        abort(400)


# Error Handling
# for 422 error
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# for 404 error
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# for 400 error
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


# for 500 error
@app.errorhandler(500)
def internal_server(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


# for auth error
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code


if __name__ == "__main__":
    app.debug = True
    app.run()
