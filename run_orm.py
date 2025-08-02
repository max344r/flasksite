from flask import Flask,render_template,g,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user,logout_user,login_required,current_user

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"]="Your Key"

db=SQLAlchemy(app)

login_manager=LoginManager(app)
login_manager.login_view="login"

class Animal(db.Model):
    __tablename__="animals"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(25),unique=True,nullable=False)
    img = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(500),nullable=False)
    data = db.Column(db.String(25), nullable=False)
    user_id=db.Column(db.Integer)
    likes=db.relationship("Like",backref="post",lazy="dynamic")

class User(UserMixin,db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(25),unique=True,nullable=False)
    email = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200))
    password =db.Column(db.String(800))
    likes = db.relationship("Like", backref="user", lazy="dynamic")

class Like(db.Model):
    __tablename__="likes"
    id=db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey("animals.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))



@app.route("/")
def index():
    animals=Animal.query.all()
    users=User.query.all()
    post_data=[]
    for animal in animals:
        likes_count=animal.likes.count()
        is_liked=False
        if current_user.is_authenticated:
            is_liked=animal.likes.filter_by(user_id=current_user.id).first() is not None
        post_data.append({
            "animals":animal,"likes_count":likes_count,"is_liked":is_liked
        })
    return render_template("index.html",animals=post_data,users=users)

@app.route("/detail/<post_id>")
def detail(post_id):
    animal=Animal.query.get(post_id)
    return render_template("detail.html",animal=animal)

@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        name = request.form["name"]
        img = request.form["img"]
        description = request.form["description"]
        data = request.form["data"]
        user_id=request.form["user_id"]

        new_animal=Animal(name=name,img=img,description=description,data=data,user_id=user_id)
        db.session.add(new_animal)
        db.session.commit()
        return redirect(url_for("index"))
    else:
        return render_template("add_post.html")

@app.route("/deleteanimal/<post_id>",methods=["POST"])
def delete_animal(post_id):
    animal=Animal.query.get(post_id)
    db.session.delete(animal)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/editanimal/<post_id>",methods=["POST","GET"])
def edit_animal(post_id):
    animal=Animal.query.get(post_id)
    if request.method=="POST":
        animal.name = request.form["name"]
        animal.img = request.form["img"]
        animal.description = request.form["description"]
        animal.data = request.form["data"]
        animal.user_id = request.form["user_id"]
        db.session.commit()
        return redirect(url_for("index"))
    else:
        return render_template("edit_post.html",post=animal)




@app.route("/users")
def users():
    users=User.query.all()
    return render_template("users.html",users=users)

@app.route("/add_user",methods=["GET","POST"])
def add_user():
    if request.method == "POST":
        username=request.form["username"]
        email=request.form["email"]
        # avatar=request.form["avatar"]
        avatar="avatar.jpg"
        password=request.form["password"]
        hash=generate_password_hash(password)
        new_user=User(username=username,email=email,avatar=avatar,password=hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("users"))
    else:
        return render_template("add_user.html")

@app.route("/profile/<username>")
def profile(username):
    return render_template("profile.html",username=username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password = request.form["password"]
        user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for("index"))
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))



@app.route("/like/<post_id>",methods=["POST"])
def like(post_id):
    animal=Animal.query.get(post_id)
    like_current=Like.query.filter_by(post_id=animal.id,user_id=current_user.id).first()
    if like_current:
        db.session.delete(like_current)
    else:
        new_like=Like(post_id=animal.id,user_id=current_user.id)
        db.session.add(new_like)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)