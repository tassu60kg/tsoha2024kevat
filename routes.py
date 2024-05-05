from flask import render_template, request, session, redirect,flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


from app import app


app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)



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
        adminstatus = isadmin()
        return render_template("index.html",score=sql,leaders = leaders, cliques=cliques, adminstatus=adminstatus)
    else:
        total = db.session.execute(text("select sum(score) from scores")).fetchone()[0]
        if not total:
            total = "No clicks :("
        sql = getthing()
        leaders = getscores()
        cliques=getscores2()
        adminstatus = isadmin()
        return render_template("index.html",score = sql,leaders = leaders,cliques=cliques,total=total, adminstatus=adminstatus)

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
        return (db.session.execute(text("select A.score from scores A, users B where A.user_id = B.id and B.username=:username"),{"username":session["username"]}).fetchone())[0]
    except:
        return 9999

def isadmin(): #checks admin status
    try:
        if db.session.execute(text("select id from users where username=:username"),{"username":session["username"]}).fetchone() in db.session.execute(text("select user_id from admins")).fetchall():
            return True
        return False
    except:
        return False
    
def isbigboss():
    try:
        userid = db.session.execute(text("select id from users where username=:username"),{"username":session["username"]}).fetchone()[0]
        if db.session.execute(text("select bigboss from admins where user_id=:userid"),{"userid":userid}).fetchone()[0] == True:
            return True
        return False
    except:
        return False

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

@app.route("/leaveclique",methods=["POST"])
def leaveclique():
    userid = getuser()
    db.session.execute(text("delete from cliques where user_id=:userid"),{"userid":userid})
    db.session.commit()
    return redirect("/cliques")

def cliquescorehelper(clique):    
    if db.session.execute(text(f"select clique from clique_score where clique = :clique"),{"clique":clique}).fetchone() == None:
        return True
    else:
        return False

@app.route("/admin",methods=["GET"])
def admin():
    if isadmin() == False:
        return redirect("/")
    bigboss = isbigboss()
    return render_template("admin.html",bigboss=bigboss)
    
@app.route("/deluser", methods=["POST"])
def deluser():
    for i in request.form.getlist("yeahimsure"):
        user = request.form["user"]
        userid = db.session.execute(text("select id from users where username=:user"),{"user":user}).fetchone()
        if userid == None:
            flash("whoopsie >__< (user not found)","warning")
            return redirect("/admin")
        userid = userid[0]
        if (userid,) in db.session.execute(text("select user_id from admins")).fetchall():
            flash("whoopsie >__< (can't delete admin)","warning")
            return redirect("/admin")
        db.session.execute(text("delete from users where id=:id"),{"id":userid})
        db.session.execute(text("delete from scores where user_id=:user_id"),{"user_id":userid})
        db.session.execute(text("delete from cliques where user_id=:user_id"),{"user_id":userid})
        db.session.commit()
        
        flash("yay ^v^ (user deleted)","warning")
        return redirect("/admin")

    flash("aborted >__< (check the box, yeah?)","warning")
    return redirect("/admin")
    


@app.route("/delclique", methods=["POST"])
def delclique():
    for i in request.form.getlist("yeahimsure"):
        clique = request.form["clique"]
        if db.session.execute(text("select clique from cliques where clique=:clique"),{"clique":clique}).fetchone() == None:
            flash("whoopsie >__< (clique not found)","warning")
            return redirect("/admin")
        db.session.execute(text("delete from cliques where clique=:clique"),{"clique":clique})
        db.session.execute(text("delete from clique_score where clique=:clique"),{"clique":clique})
        db.session.commit()

        flash("yay ^v^ (clique deleted)","warning")
        return redirect("/admin")

    flash("aborted >__< (check the box, yeah?)","warning")
    return redirect("/admin")


@app.route("/deladmin", methods=["POST"])
def deladmin():
    for i in request.form.getlist("yeahimsure"):
        user = request.form["user"]
        userid = db.session.execute(text("select id from users where username=:user"),{"user":user}).fetchone()
        if userid == None:
            flash("whoopsie >__< (user not found)","warning")
            return redirect("/admin")
        userid = userid[0]
        db.session.execute(text("delete from admins where user_id=:user_id"),{"user_id":userid})
        db.session.commit()
        flash("yay ^v^ (admin privliges revoked)","warning")
        return redirect("/admin")

    flash("aborted >__< (check the box, yeah?)","warning")
    return redirect("/admin")

@app.route("/giveadmin", methods=["POST"])
def giveadmin():
    for i in request.form.getlist("yeahimsure"):
        user = request.form["user"]
        userid = db.session.execute(text("select id from users where username=:user"),{"user":user}).fetchone()
        if userid == None:
            flash("whoopsie >__< (user not found)","warning")
            return redirect("/admin")
        userid = userid[0]
        for i in request.form.getlist("bigboss"):
            db.session.execute(text("insert into admins (user_id,bigboss) values (:user_id,True) "),{"user_id":userid})
            db.session.commit()
            flash(f"yay ^v^ (big boss privliges given to {user})","warning")
            return redirect("/admin")
        db.session.execute(text("insert into admins (user_id,bigboss) values (:user_id,False) "),{"user_id":userid})
        db.session.commit()
        flash(f"yay ^v^ (admin privliges given to {user})","warning")
        return redirect("/admin")

    flash("aborted >__< (check the box, yeah?)","warning")
    return redirect("/admin")



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
    
