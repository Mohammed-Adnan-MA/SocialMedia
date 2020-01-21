import requests, os, json
from flask import Flask, render_template, request, jsonify, session, make_response, url_for, redirect, flash
from config import Config
from flask_migrate import Migrate
from flask_api import FlaskAPI
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_bootstrap import Bootstrap
#from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from models import *

#csrf = CSRFProtect(app)
#session(app)
sess = Session()
app.secret_key = "supersecretkey"
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = b'{\x06\xad;\x93+P\xed-l\xed\xf05\xcd\xb0\xe6'
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User_Info.query.get(int(user_id))

###########################################################################

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

###########################################################################

@app.route("/loadposts")
def loadPosts():
    postsImport = Posts.query.all()
    commentsImport = []
    #usernameImport = User_Info.query.with_entities(User_Info.username, User_Info.id).all()
    usernameExport = []
    commentUsernameExport = []
    posts_schema = PostsSchema(many=True)
    comments_schema = CommentsSchema(many=True)
    postsExport = posts_schema.dump(postsImport)
    
    
    
    for i in postsImport:
        print(i.id)
        for j in User_Info.query.with_entities(User_Info.username, User_Info.id).all():
            if i.post_author_id == j.id:
                usernameExport.append(j.username)
        for counter in Comments.query.all():
            if i.id == counter.post_comments_id:
                commentsImport.append(counter)
                
    commentsExport = comments_schema.dump(commentsImport)
    print(commentsImport)

    for i in Comments.query.all():
        for j in User_Info.query.with_entities(User_Info.username, User_Info.id).all():
            if i.comment_author_id == j.id:
                commentUsernameExport.append(j.username)

    if current_user.is_authenticated:
        currentCommentNeedingInfo = {"user_id": current_user.id, "username": current_user.username, "state": "true"}
    else:
        currentCommentNeedingInfo = {"state": "Not authorized"}                       
    
    return jsonify({
                    "posts": postsExport,
                    "postUsername": usernameExport,
                    "comments": commentsExport,
                    "commentUsername": commentUsernameExport,
                    "newCommentDetails": currentCommentNeedingInfo
                    })

###########################################################################


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for('account'))
        return render_template("signup.html")
    if current_user.is_authenticated:
        return redirect(url_for('home'))  

    # Get form information.
    if request.get_json() != None:
        req = request.get_json()
        username = req["username"]
        fName = req["fname"]
        lName = req["lname"]
        gender = req["gender"]
        birthDate = req["birthDate"]
        phoneNo = req["phoneNo"]
        password = generate_password_hash(req["password"])

        m = User_Info(username = username, first_name = fName, last_name = lName, phone_no = phoneNo, gender = gender,
                 date_of_birth = birthDate, password_hash = password)


        db.session.add(m)        
        db.session.commit()

        #flash('Your account has been created! You are now able to log in', 'success')
    return redirect(url_for("login"))    
   

###########################################################################     

@app.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        return render_template("login.html")    

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.get_json() != None:
        req = request.get_json()
        phoneNo = req["phoneNo"]
        password = req["password"]
        rememberMe =  req["rememberMe"]

        user = User_Info.query.filter_by(phone_no=phoneNo).first()
        if user:
            if check_password_hash(user.password_hash, password):
                login_user(user, remember = rememberMe)
                return (make_response(jsonify({"message": "JSON received!"}), 200))
        else:
            return make_response(jsonify({"message": "error"}), 422)
    return render_template("home.html")

###########################################################################    

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

###########################################################################

@app.route('/account-info')
def accountInfo():
    #Still under development
    if current_user.is_authenticated:
        userInfo = {"user_id":current_user.id, "username":current_user.username, "first_name":current_user.first_name,
                    "last_name":current_user.last_name, "phone_no":current_user.phone_no}

        return jsonify({
            "userInfo": userInfo
        })

    return jsonify({"error": "Invalid username"}), 422    

###########################################################################

@app.route("/api/postinfo/<post_id>")
@login_required
def postQuery(post_id):
    if request.get_json() != None:     
        for i in Posts.query.filter_by(post_author_id = current_user.id):
            if i.id == User_Info.id:
                return jsonify({
                        "body": i.body,
                        "imgURL": i.img_url
                    })
    return make_response(jsonify({"message": "error"}), 422)

###########################################################################    

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    #Still under development

    if request.method == "GET":
        if current_user.is_authenticated:
            return render_template("create_post.html")
        return("You have to login at first!")
    if request.get_json() != None:
        req = request.get_json()
        body = req["body"]
        if req["img"] != "":
            img = req["img"]
            post = Posts(body = body, img_url = img, post_author = current_user)
        else:
            post = Posts(body = body, post_author = current_user)

        db.session.add(post)
        db.session.commit()
        return make_response(jsonify({"message": "JSON received!"}), 200)
    return make_response(jsonify({"message": "error"}), 422)

###########################################################################    


@app.route("/store-new-comments", methods=['GET','POST'])
@login_required
def storeNewComments():
    if request.method == "GET":
        return redirect(url_for("home"))
    if request.get_json() != None:
        req = request.get_json()
        comment = req["comment"]
        postCommentId = req["whichPost"]
        storeComment = Comments(comment = comment, comment_author = current_user, post_comments_id = postCommentId)

        db.session.add(storeComment)
        db.session.commit()
        return make_response(jsonify({"message": "JSON received!"}), 200)
    return make_response(jsonify({"message": "error"}), 422)

###########################################################################

@app.route("/post/update/<int:post_id>", methods=['GET','POST'])
@login_required
def update_post(post_id):
    #Still under development

    if request.get_json() != None:
        req = request.get_json()
        body = req["body"]
        imgURL = req["imageURL"]

        post = Posts.query.get_or_404(post_id)

    return render_template('create_post.html', legend='Update Post')

###########################################################################

@app.route("/about")
def about():
    #Still under development

    return render_template("about.html")    

###########################################################################

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))    
