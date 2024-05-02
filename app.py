from crypt import methods
import imp
from flask import Flask, redirect,flash
#idk why redirect is there twice
from flask import render_template, request, session, redirect
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect,CSRFError



#TODO comment code, remove finnish, maybe find better variable names (last one maybe not)
app=Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
csrf = CSRFProtect()


def create_app():
    csrf.init_app(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400



#this setup uses a hidden form (bad idea), if you know a better way please tell me 
@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "POST":
        score = request.form.get('formthing')
        #dw about the errors

        #this part changes the users score
        userid = db.session.execute(text(f"select id from users where username = :username"),{"username":session["username"]}).fetchone()[0]
        newscore =int(score) + int(db.session.execute(text(f"select score from scores where user_id = :userid"),{"userid":userid}).fetchone()[0])
        db.session.execute(text(f"delete from scores where user_id = {userid}"))
        db.session.execute(text(f"insert into scores (score, user_id) values (:newscore,:userid)"),{"newscore":newscore,"userid":userid})

        #this changes the cliques score
        cliquescorechanger(userid,score)

        db.session.commit()
        #print(userid,newscore)
        sql = getthing()
        leaders = getscores()
        #print(sql,"sql")
        cliques=getscores2()
        return render_template("index.html",score=sql,leaders = leaders, cliques=cliques )
    else:
        sql = getthing()
        leaders = getscores()
        cliques=getscores2()
        return render_template("index.html",score = sql,leaders = leaders,cliques=cliques)

def cliquescorechanger(userid,score):
    try:
        userclique = db.session.execute(text("select clique from cliques where user_id = :userid"),{"userid":userid}).fetchone()[0]
        newcliquescore = int(score) + int(db.session.execute(text("select score from clique_score where clique = :clique"),{"clique":userclique}).fetchone()[0])
        db.session.execute(text("delete from clique_score where clique=:clique"),{"clique":userclique})
        db.session.execute(text("insert into clique_score (clique,score) values (:clique,:score)"),{"clique":userclique,"score":newcliquescore})
    except:
        pass

def getthing(): #gets user score
    try:
        xd = f"select A.score from scores A, users B where A.user_id = B.id and B.username=:username"
        return (db.session.execute(text(xd),{"username":session["username"]}).fetchone())[0]
    except:
        return 9999

def getuser(): #gets user id
    try:
        return db.session.execute(text(f"select id from users where username = :username"),{"username":session["username"]}).fetchone()[0]
    except:
        return None
def getscores(): #gets top 10 users
    return db.session.execute(text("select A.username, B.score from users A, scores B where A.id = B.user_id order by score desc limit 10")).fetchall()
def getscores2(): #gets top 10 cliques
    return db.session.execute(text("select clique,score from clique_score order by score desc limit 10")).fetchall()

@app.route("/cliques",methods=["POST","GET"])
def cliques():
    if request.method == "POST":
        clique = request.form["clique"]
        if len(clique) < 1:
            flash("whoopsie >__< (need name)","warning")
            return redirect("/cliques")
        if len(clique) > 100:
            flash("whoopsie >__< (name too long)","warning")
            return redirect("/cliques")
        userid = getuser()
        if db.session.execute(text("select clique from cliques where user_id = :userid"),{"userid":userid}).fetchone() != None:
            flash("whoopsie >__< (already joined)","warning")
            return redirect("/cliques")
        #userid = db.session.execute(text(f"select id from users where username = :username"),{"username":session["username"]}).fetchone()[0]
        sql = f"insert into cliques (user_id,clique) values (:userid,:clique)"
        db.session.execute(text(sql), {"userid":userid, "clique":clique})
        if cliquescorehelper(clique):
            sql2 = f"insert into clique_score (clique,score) values (:clique,:score)"
            db.session.execute(text(sql2),{"clique":clique,"score":0})
        db.session.commit()

        return redirect("/")
    else:
        userid = getuser()
        if db.session.execute(text("select clique from cliques where user_id = :userid"),{"userid":userid}).fetchone() != None:
            userclique = db.session.execute(text("select clique from cliques where user_id = :userid"),{"userid":userid}).fetchone()[0]
            return render_template("cliques.html",userclique=userclique)
        else:
            return render_template("cliques.html",userclique="none :(")
def cliquescorehelper(clique):    
    if db.session.execute(text(f"select clique from clique_score where clique = :clique"),{"clique":clique}).fetchone() == None:
        return True
    else:
        return False

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT id, password FROM users WHERE username=:username"
        result = db.session.execute(text(sql), {"username":username})
        user = result.fetchone()    
        if not user:
            flash("whoopsie >__< (wrong username or password)","warning")
            return redirect("/login")
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
                session["username"]=username
            else:
                flash("whoopsie >__< (wrong username or password)","warning")
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
            flash("whoopsie >__< (need username and/or password)","warning")
            return redirect("/signup")
        if len(password) > 25 or len(username) > 100:
            flash("whoopsie >__< (username or password too long)","warning")
            return redirect("/signup")
        if db.session.execute(text("SELECT username FROM users WHERE username=:username"), {"username":username}).fetchone() != None:
            flash("whoopsie >__< (user exists already)","warning")
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
    
