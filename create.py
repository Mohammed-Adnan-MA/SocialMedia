from flask import Flask, request
from models import *

app= Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ("postgresql://postgres:1234@localhost/SocialMediaDB")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)



def main():
    db.create_all()
    

if __name__ == "__main__":
    with app.app_context():
        main()
