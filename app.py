

from flask import (
    Flask, render_template, request,
    redirect, url_for, jsonify, session
)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime, timezone
from functools import wraps
from getpass import getpass

import os
import random


# ==================================
# 1. FLASK APPLICATION
# ==================================

app = Flask(__name__)
@app.before_request
def log_session():
    print(f"[SESSION INFO] SessionID: {session.sid}")

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "local-development-secret-change-before-deployment"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vibecheck.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==================================
# 2. ADMIN LOGIN SYSTEM
# ==================================

login_manager = LoginManager(app)
login_manager.login_view = "admin_login"


class Admin(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


# ==================================
# 3. VISITOR DATABASE
# ==================================

class Visitor(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(40),
        nullable=False
    )

    username = db.Column(
        db.String(30),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ==================================
# 4. LOAD ADMIN USER
# ==================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(Admin, int(user_id))


# ==================================
# 5. ADMIN SECURITY
# ==================================

def admin_required(function):

    @wraps(function)
    @login_required
    def wrapper(*args, **kwargs):

        return function(*args, **kwargs)

    return wrapper


# ==================================
# 6. HOME PAGE
# ==================================

@app.route("/")
def home():

    return render_template("index.html")


# ==================================
# 7. VIBE ANALYZER
# ==================================

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}

    # Consent verification
    if data.get("consent") is not True:

        return jsonify({
            "error": "Please agree to the data collection notice."
        }), 400

    # Visitor details
    name = (data.get("name") or "").strip()

    username = (
        (data.get("username") or "")
        .strip()
        .lstrip("@")
    )

    if not name or len(name) > 40 or len(username) > 30:

        return jsonify({
            "error": "Please enter valid details."
        }), 400

    hobby = (data.get("hobby") or "Music").strip()[:80]

    personality = (
        data.get("personality") or "Chill"
    ).strip()[:40]

    mood = (
        data.get("mood") or "Happy"
    ).strip()[:40]

    # Save visitor in database
    visitor = Visitor(
        name=name,
        username=username or None
    )

    db.session.add(visitor)
    db.session.commit()

    # Generate vibe report
    seed = f"{name}{username}{hobby}{personality}{mood}"

    rng = random.Random(seed)

    result = {

        "name": name,

        "username": (
            "@" + username if username else ""
        ),

        "vibe": rng.choice([
            "Main Character Energy",
            "Golden Heart",
            "Comedy Superstar",
            "Certified Chaos Creator"
        ]),

        "score": rng.randint(75, 99),

        "funny": rng.choice([
            "Your brain has 100 tabs open!",
            "Your plans are legendary!",
            "You make boring moments interesting!"
        ]),

        "compliment": rng.choice([
            "You have a beautiful personality!",
            "You bring positive energy!",
            "Your creativity is your superpower!"
        ]),

        "roast": rng.choice([
            "Your reply speed is slower than WiFi!",
            "Your confidence has unlimited battery!",
            "Your plans need a loading screen!"
        ]),

        "cute": rng.choice([
            "You secretly care a lot!",
            "You make little moments special!",
            "You have a sweet side!"
        ]),

        "verdict": "Keep shining and spreading good vibes!"
    }

    return jsonify(result)


# ==================================
# 8. ADMIN LOGIN PAGE
# ==================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password, password
        ):

            login_user(admin)

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "admin_login.html",
            error="Invalid login details"
        )

    return render_template("admin_login.html")


# ==================================
# 9. ADMIN DASHBOARD
# ==================================

@app.route("/admin/dashboard")
@admin_required
def dashboard():

    visitors = Visitor.query.order_by(
        Visitor.created_at.desc()
    ).limit(100).all()

    total_visitors = Visitor.query.count()

    return render_template(
        "dashboard.html",
        visitors=visitors,
        total_visitors=total_visitors
    )


# ==================================
# 10. ADMIN LOGOUT
# ==================================

@app.route("/admin/logout")
@admin_required
def admin_logout():

    logout_user()

    return redirect(
        url_for("admin_login")
    )


# ==================================
# 11. CREATE ADMIN ACCOUNT
# ==================================

@app.cli.command("create-admin")
def create_admin():

    db.create_all()

    username = input(
        "Enter admin username: "
    ).strip()

    password = getpass(
        "Enter admin password: "
    )

    if not username or len(password) < 12:

        print(
            "Username required. Password must be at least 12 characters."
        )

        return

    existing_admin = Admin.query.filter_by(
        username=username
    ).first()

    if existing_admin:

        print("Admin account already exists.")

        return

    admin = Admin(

        username=username,

        password=generate_password_hash(password)

    )

    db.session.add(admin)

    db.session.commit()

    print("Admin account created successfully!")


# ==================================
# 12. RUN APPLICATION
# ==================================

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False)
