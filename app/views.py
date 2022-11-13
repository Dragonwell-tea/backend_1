from functools import wraps
from time import time as now
import uuid
import re

import flask
import schema
import bcrypt
import jwt

from .models import Category, Product, UserRole, db, User


blueprint = flask.Blueprint("views", __name__)


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE


def create_token(expires_in=1 * HOUR, **kwargs):
    private_key = flask.current_app.config["JWT_PRIVATE_KEY"]
    algorithm = flask.current_app.config["JWT_ALGORITHM"]
    return jwt.encode(
        {"iat": now(), "exp": now() + expires_in, **kwargs},
        private_key,
        algorithm=algorithm,
    )


def token_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "Authorization" not in flask.request.headers:
            return {"status": "Forbidden"}, 403
        header = flask.request.headers["Authorization"]
        parse = re.match(r"Bearer (.*)", header)
        if not parse:
            return {"status": "Forbidden"}, 403
        (token,) = parse.groups()
        try:
            public_key = flask.current_app.config["JWT_PUBLIC_KEY"]
            algorithm = flask.current_app.config["JWT_ALGORITHM"]
            claims = jwt.decode(token, public_key, algorithms=[algorithm])
        except:
            return {"status": "Forbidden"}, 403
        flask.g.token = claims
        return f(*args, **kwargs)

    return inner


EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


def is_email(email_address):
    return re.fullmatch(EMAIL_REGEX, email_address)


REGISTER_SCHEMA = schema.Schema(
    {
        "user_name": schema.And(str, len),
        "password": schema.And(str, len),
        "phone": schema.And(str, len),
        "email": schema.And(str, len, is_email),
    }
)


@blueprint.route("/register", methods=["POST"])
def register_route():
    if not isinstance(flask.request.json, dict):
        return {"status": "Bad request"}, 400
    try:
        request = REGISTER_SCHEMA.validate(flask.request.json.copy())
    except schema.SchemaError as error:
        return {"status": "Bad request", "message": str(error)}, 400

    email = request["email"]
    user_name = request["user_name"]
    password = request["password"]
    phone = request["phone"]

    if db.session.query(User).filter(User.email == email).first():
        return {"status": "Email is already exsit"}, 409

    user = User()
    user.user_id = str(uuid.uuid4())
    user.email = email
    user.phone = phone
    user.role = UserRole.user.value
    user.user_name = user_name
    user.hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.session.merge(user)
    db.session.commit()

    user = db.session.get(User, user.user_id)
    return flask.jsonify({"token": create_token(**user.to_dict())})


LOGIN_SCHEMA = schema.Schema(
    {"user_name": schema.And(str, len), "password": schema.And(str, len)}
)


@blueprint.route("/login", methods=["POST"])
def login_route():
    if not isinstance(flask.request.json, dict):
        return {"status": "Bad request"}, 400
    try:
        request = LOGIN_SCHEMA.validate(flask.request.json.copy())
    except schema.SchemaError as error:
        return {"status": "Bad request", "message": str(error)}, 400

    user_name = request["user_name"]
    password = request["password"]

    user = db.session.query(User).filter(User.user_name == user_name).first()
    if user is None:
        return {"status": "Unauthorized"}, 401
    if not bcrypt.checkpw(password.encode(), user.hash.encode()):
        return {"status": "Unauthorized"}, 401
    return flask.jsonify({"token": create_token(**user.to_dict())})


@blueprint.route("/currentUser", methods=["GET"])
@token_required
def current_user_route():
    current_user_id = flask.g.token["user_id"]
    current_user = db.session.get(User, current_user_id)
    return flask.jsonify(current_user.to_dict())


@blueprint.route("/category", methods=["GET"])
@token_required
def get_categories_route():
    categories = db.session.query(Category)
    response = [{**m.to_dict()} for m in categories]
    return flask.jsonify(response)


@blueprint.route("/product", methods=["GET"])
def get_products_route():
    products = db.session.query(Product)
    response = [{**m.to_dict()} for m in products]
    return flask.jsonify(response)


@blueprint.route("/product/<product_id>", methods=["GET"])
def get_product_route(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return {"status": "Not Found"}, 404
    return flask.jsonify(product.to_dict())


CREATE_PRODUCT_SCHEMA = schema.Schema(
    {
        "product_name": schema.And(str, len),
        "picture": schema.And(str, len),
        "selling_price": schema.And(schema.Use(float), lambda i: i >= 0),
        "description": schema.And(str, len),
        "category_id": schema.And(schema.Use(int), lambda i: i >= 0),
    }
)


@blueprint.route("/product", methods=["POST"])
@token_required
def create_product_route():
    try:
        request = CREATE_PRODUCT_SCHEMA.validate(flask.request.json.copy())
    except schema.SchemaError as error:
        return {"status": "Bad request", "message": str(error)}, 400

    product = Product()
    product.product_name = request["product_name"]
    product.picture = request["picture"]
    product.selling_price = request["selling_price"]
    product.description = request["description"]
    product.available = 0
    product.category_id = request["category_id"]
    product.user_id = flask.g.token["user_id"]
    db.session.add(product)
    db.session.commit()

    return flask.jsonify({"message": "success"})


UPDATE_PRODUCT_SCHEMA = schema.Schema(
    {
        "product_id": schema.And(schema.Use(int), lambda i: i >= 0),
        "product_name": schema.And(str, len),
        "picture": schema.And(str, len),
        "selling_price": schema.And(schema.Use(float), lambda i: i >= 0),
        "description": schema.And(str, len),
        "category_id": schema.And(schema.Use(int), lambda i: i >= 0),
    }
)


@blueprint.route("/product", methods=["PUT"])
@token_required
def update_product_route():
    try:
        request = UPDATE_PRODUCT_SCHEMA.validate(flask.request.json.copy())
    except schema.SchemaError as error:
        return {"status": "Bad request", "message": str(error)}, 400

    current_user_id = flask.g.token["user_id"]
    product = db.session.get(Product, request["product_id"])
    if not product:
        return {"status": "Not Found"}, 404
    if product.user_id != current_user_id:
        return {"status": "Permission denied"}, 401

    for k in request:
        if k == "product_name":
            product.product_name = request["product_name"]
        elif k == "picture":
            product.picture = request["picture"]
        elif k == "selling_price":
            product.selling_price = request["selling_price"]
        elif k == "description":
            product.description = request["description"]
        elif k == "category_id":
            product.category_id = request["category_id"]

    db.session.merge(product)
    db.session.commit()

    return flask.jsonify({"message": "success"})


@blueprint.route("/product/<product_id>", methods=["DELETE"])
@token_required
def delete_product_route(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return {"status": "Not Found"}, 404

    current_user_id = flask.g.token["user_id"]
    if product.user_id != current_user_id:
        return {"status": "Permission denied"}, 401

    db.session.delete(product)
    db.session.commit()
    return flask.jsonify({"message": "success"})
