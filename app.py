from crypt import methods
from flask import Flask, redirect,flash
#emt why redirect is 2 times
from flask import render_template, request, session, redirect
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from secrets import token_hex


#TODO comment code, remove finnish, maybe find better variable names (last one maybe not)
app=Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

#this setup uses a hidden form (bad idea), if you know a better way please tell me 
@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "POST":
        score = request.form.get('formthing')
        #these errors should't be a problem?
        userid = db.session.execute(text(f"select id from users where username = :username"),{"username":session["username"]}).fetchone()[0]
        newscore =int(score) + int(db.session.execute(text(f"select score from scores where user_id = :userid"),{"userid":userid}).fetchone()[0])
        db.session.execute(text(f"delete from scores where user_id = {userid}"))
        db.session.execute(text(f"insert into scores (score, user_id) values (:newscore,:userid)"),{"newscore":newscore,"userid":userid})
        db.session.commit()
        print(userid,newscore)
        sql = getthing()
        leaders = getscores()
        print(sql,"sql")
        return render_template("index.html",score=sql,leaders = leaders)
    else:
        sql = getthing()
        leaders = getscores()
        cliques=getscores2()
        return render_template("index.html",score = sql,leaders = leaders,cliques=cliques)

def getthing():
    try:
        xd = f"select A.score from scores A, users B where A.user_id = B.id and B.username=:username"
        return (db.session.execute(text(xd),{"username":session["username"]}).fetchone())[0]
    except:
        return 9999

    
def getscores():
    return db.session.execute(text("select A.username, B.score from users A, scores B where A.id = B.user_id order by score desc limit 10")).fetchall()
def getscores2():
    return db.session.execute(text("select clique,score from clique_score order by clique_score limit 10")).fetchall()

@app.route("/cliques",methods=["POST","GET"])
def cliques():
    if request.method == "POST":
        clique = request.form["clique"]
        if len(clique) < 1:
            flash("tyhmä🖕 (need name)","warning")
            return redirect("/cliques")
        userid = db.session.execute(text(f"select id from users where username = :username"),{"username":session["username"]}).fetchone()[0]
        sql = f"insert into cliques (user_id,clique) values (:userid,:clique)"
        db.session.execute(text(sql), {"userid":userid, "clique":clique})
        if cliquescorehelper(clique):
            sql2 = f"insert into clique_score (clique,score) values (:clique,:score)"
            db.session.execute(text(sql2),{"clique":clique,"score":0})
        db.session.commit()

        return redirect("/")
    else:
        return render_template("cliques.html")

def cliquescorehelper(clique):
    try:
        if db.session.execute(text(f"select clique from clique_score where clique = :clique"),{"clique":clique}).fetchone() == None:
            return True
        else:
            return False
    except:
        return True
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT id, password FROM users WHERE username=:username"
        result = db.session.execute(text(sql), {"username":username})
        user = result.fetchone()    
        if not user:
            flash("tyhmä🖕 (this problem was your fault)","warning")
            return redirect("/login")
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                session["username"]=username
            else:
                flash("tyhmä🖕 (this problem was your fault)","warning")
                return redirect("/login")
        
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
        if len(password) < 1 or len(username) < 1:
            flash("tyhmä🖕 (need username and/or password)","warning")
            return redirect("/signup")
        if len(password) > 25 or len(username) > 100:
            flash("tyhmä🖕 (username or password too long)","warning")
            return redirect("/signup")
        if db.session.execute(text("SELECT username FROM users WHERE username=:username"), {"username":username}).fetchone() != None:
            flash("tyhmä🖕 (user exists already)","warning")
            return redirect("/signup")
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(text(sql), {"username":username, "password":hash_value})
        id = db.session.execute(text("select id from users where username = :username"),{"username":username}).fetchone()[0]
        sql2 = f"insert into scores (score,user_id) values (0,{id})"
        db.session.execute(text(sql2))

        db.session.commit()
        return redirect("/")
        
    else:
        return render_template("signup.html")
    
