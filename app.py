from crypt import methods
from flask import Flask, redirect
from flask import render_template, request, session, redirect
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

#TODO comment code, remove finnish, maybe find better variable names
app=Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)


@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "POST":
        
        #db.session.execute(text(f"insert into scores (score,user_id) values (100,100)"))
        score = request.form.get('formthing')
        #these errors should't be a problem?
        userid = db.session.execute(text(f"select id from users where username = '{session['username']}'")).fetchone()[0]
        newscore =int(score) + int(db.session.execute(text(f"select score from scores where user_id = '{userid}'")).fetchone()[0])
        db.session.execute(text(f"delete from scores where user_id = {userid}"))
        db.session.execute(text(f"insert into scores (score, user_id) values ({newscore},{userid})"))
        db.session.commit()
        print(userid,newscore)
        sql = getthing()
        print(sql,"sql")
        return render_template("index.html",score=sql)
    else:
        sql = getthing()
        leaders = getscores()
        #fix that below
        return render_template("index.html",score = sql,leaders = leaders)

def getthing():
    try:
        xd = f"select A.score from scores A, users B where A.user_id = B.id and B.username = '{session['username']}'"
        return (db.session.execute(text(xd)).fetchone())[0]
    except:
        return 9999
    
def getscores():
    return db.session.execute(text("select A.username, B.score from users A, scores B where A.id = B.user_id order by score desc")).fetchall()
    


@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT id, password FROM users WHERE username=:username"
        result = db.session.execute(text(sql), {"username":username})
        user = result.fetchone()    
        if not user:
            redirect("/login")
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                session["username"]=username
            else:
                redirect("/login")
        
        return redirect("/")
        
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(text(sql), {"username":username, "password":hash_value})
        id = db.session.execute(text(f"select id from users where username = '{username}'")).fetchone()[0]
        sql2 = f"insert into scores (score,user_id) values (0,{id})"
        db.session.execute(text(sql2))

        db.session.commit()
        return redirect("/")
        
    else:
        return render_template("signup.html")
    
