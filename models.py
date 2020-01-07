import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ("postgresql://postgres:1234@localhost/SocialMediaDB")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)



class User_Info(UserMixin, db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    phone_no = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(2), nullable=False)
    date_of_birth = db.Column(db.DATE, nullable=False)
    profile_img_url = db.Column(db.LargeBinary, nullable=True)
    password_hash = db.Column(db.String(300), nullable=False)
    post = db.relationship("Posts", backref="post_author", lazy=True)
    comment = db.relationship("Comments", backref="comment_author", lazy=True)

class Posts(db.Model):
    __tablename__ = "posts"
    id =  db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(150), nullable=False)
    img_url = db.Column(db.LargeBinary, nullable=True)
    post_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    postComments = db.relationship("Comments", backref="post_comments", lazy=True)
    post_author_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False)
    

class Comments(db.Model):
    __tablename__ = "comments"
    id =  db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(150), nullable=False)
    comment_date = db.Column(db.DateTime, default=datetime.utcnow) 
    comment_author_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False)
    post_comments_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)    
    
class User_InfoSchema(ma.ModelSchema):
    class Meta:
        model = User_Info

class PostsSchema(ma.ModelSchema):
    class Meta:
        model = Posts

class CommentsSchema(ma.ModelSchema):
    class Meta:
        model = Comments


with app.app_context():
    db.create_all()