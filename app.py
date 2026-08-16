import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///samtechacademy.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_globals():
    return {
        "business_name": "SAMTECHACADEMY",
        "tagline": "Connecting Students to Digital Opportunities",
        "contact_email": "samotienoapiyo@gmail.com",
        "whatsapp": "+254711733456",
    }

@app.route("/")
def home():
    opportunities = Opportunity.query.order_by(Opportunity.id.desc()).limit(6).all()
    return render_template("home.html", opportunities=opportunities)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    service_list = [
        ("Academic Writing Guidance", "Support with structure, research planning and academic presentation."),
        ("Research Assistance", "Research planning, literature organization and project guidance."),
        ("CV & Resume Writing", "Professional CV improvement and career-document support."),
        ("LinkedIn Optimization", "Improve your professional profile and online presence."),
        ("Data Annotation Support", "Guidance for legitimate data-labeling and AI training projects."),
        ("AI Training Project Guidance", "Learn practical workflows used in AI and data projects."),
        ("Website Development", "Modern websites for students, entrepreneurs and small businesses."),
        ("Computer Science Tutoring", "Practical support in programming, databases and web development."),
        ("Digital Skills Training", "Build useful digital and productivity skills."),
    ]
    return render_template("services.html", services=service_list)

@app.route("/opportunities")
def opportunities():
    items = Opportunity.query.order_by(Opportunity.id.desc()).all()
    return render_template("opportunities.html", opportunities=items)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please fill in all fields.", "error")
        else:
            db.session.add(Message(name=name, email=email, message=message))
            db.session.commit()
            flash("Your message has been sent successfully.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("All fields are required.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        else:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["is_admin"] = user.is_admin
            return redirect(url_for("admin" if user.is_admin else "home"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():
    users = User.query.order_by(User.id.desc()).all()
    opportunities = Opportunity.query.order_by(Opportunity.id.desc()).all()
    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template("admin.html", users=users, opportunities=opportunities, messages=messages)

@app.route("/admin/opportunity/new", methods=["POST"])
@admin_required
def add_opportunity():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    link = request.form.get("link", "").strip()
    if title and category and description:
        db.session.add(Opportunity(title=title, category=category, description=description, link=link))
        db.session.commit()
        flash("Opportunity added.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/opportunity/<int:item_id>/delete", methods=["POST"])
@admin_required
def delete_opportunity(item_id):
    item = db.get_or_404(Opportunity, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Opportunity deleted.", "success")
    return redirect(url_for("admin"))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized.")

@app.cli.command("create-admin")
def create_admin():
    email = os.getenv("ADMIN_EMAIL", "samotienoapiyo@gmail.com")
    password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
    name = os.getenv("ADMIN_NAME", "Sam Apiyo")
    if User.query.filter_by(email=email).first():
        print("Admin already exists.")
        return
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    print(f"Admin created for {email}. Change the password immediately.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
