import flask_sqlalchemy
from enum import Enum


db = flask_sqlalchemy.SQLAlchemy()


class UserRole(Enum):
    user = 0
    admin = 1

class ProductAvailable(Enum):
    unsold: 0
    sold: 1


class OrderStatus(Enum):
    waitCheck: 0
    checked: 1
    finish: 2


class User(db.Model):
    user_id = db.Column(db.VARCHAR(100), primary_key=True)
    user_name = db.Column(db.TEXT)
    phone = db.Column(db.TEXT)
    role = db.Column(db.INTEGER)
    email = db.Column(db.VARCHAR(100), unique=True)
    profile_picture = db.Column(db.TEXT)
    hash = db.Column(db.TEXT)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "phone": self.phone,
            "role": self.role,
            "email": self.email,
            "profile_picture": self.profile_picture,
        }


class Category(db.Model):
    category_id = db.Column(db.BIGINT, primary_key=True)
    category_name = db.Column(db.TEXT)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
        }


class Product(db.Model):
    product_id = db.Column(db.BIGINT, primary_key=True)
    product_name = db.Column(db.TEXT)
    picture = db.Column(db.TEXT)
    selling_price = db.Column(db.FLOAT)
    description = db.Column(db.TEXT)
    available = db.Column(db.INTEGER)
    user_id = db.Column(db.ForeignKey(User.user_id))
    category_id = db.Column(db.ForeignKey(Category.category_id))
    category = db.relationship("Category")

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "picture": self.picture,
            "selling_price": self.selling_price,
            "description": self.description,
            "available": self.available,
            "user_id": self.user_id,
            "category": self.category.category_name,
        }


class Order(db.Model):
    order_id = db.Column(db.BIGINT, primary_key=True)
    status = db.Column(db.INTEGER)
    create_date = db.Column(db.TIMESTAMP)
    user_id = db.Column(db.ForeignKey(User.user_id))
    product_id = db.Column(db.ForeignKey(Product.product_id))
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "status": self.status,
            "create_date": self.create_date,
            "user_id": self.user_id,
            "product_id": self.product_id,
        }
