from flask import Flask, render_template, request, session, redirect,flash
from os import getenv
from flask_wtf.csrf import CSRFProtect,CSRFError


app=Flask(__name__)
app.secret_key = getenv("SECRET_KEY")


csrf = CSRFProtect()
csrf.init_app(app)

import routes

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400



