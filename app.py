from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "skatebikes_secret_key"

# ====== Conexión MongoDB ======
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["skatebikes"]
usuarios_collection = db["usuarios"]

# ====== RUTAS ======

@app.route("/")
def index():
    return render_template("index.html")

# ----- Registro -----
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        usuario = request.form["usuario"]
        password = request.form["password"]
        confirmar = request.form["confirmar"]

        if password != confirmar:
            flash("Las contraseñas no coinciden")
            return redirect(url_for("register"))

        if usuarios_collection.find_one({"usuario": usuario}) or usuarios_collection.find_one({"email": email}):
            flash("El usuario o correo ya está registrado")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        usuarios_collection.insert_one({
            "nombre": nombre,
            "email": email,
            "usuario": usuario,
            "password": password_hash
        })

        flash("Registro exitoso. Ya puedes iniciar sesión.")
        return redirect(url_for("login"))

    return render_template("register.html")

# ----- Login -----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        user = usuarios_collection.find_one({"usuario": usuario})

        if user and check_password_hash(user["password"], password):
            session["usuario"] = user["usuario"]
            session["nombre"] = user["nombre"]
            flash(f"Bienvenido {user['nombre']}")
            return redirect(url_for("perfil"))
        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("login"))

    return render_template("login.html")

# ----- Perfil -----
@app.route("/perfil")
def perfil():
    if "usuario" in session:
        return render_template("perfil.html", nombre=session["nombre"])
    else:
        flash("Debes iniciar sesión primero.")
        return redirect(url_for("login"))

# ----- Logout -----
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
