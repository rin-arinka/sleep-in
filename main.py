from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB with the UserMixin
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    role: Mapped[str] = mapped_column(String(1000))

with app.app_context():
    db.create_all()

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)

@app.route("/about")
def about():
    return render_template("landing-page/about.html", logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("landing-page/contact.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)

            if user.role == 'admin':
                return redirect(url_for('dashboard_admin'))

            else:
                return redirect(url_for('dashboard'))

    # Passing True or False if the user is authenticated.
    return render_template("authentications/login.html", logged_in=current_user.is_authenticated)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        result = db.session.execute(db.select(User).where(User.email == email))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('sign_up'))

        # Hashing and salting the password entered by the user
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Storing the hashed password in our database
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
            role='user',
        )

        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)

        # Can redirect() and get name from the current_user
        return redirect(url_for("dashboard"))

    return render_template("authentications/sign_up.html", logged_in=current_user.is_authenticated)

# Only logged-in users can access the route
@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-user/dashboard.html", name=current_user.name, logged_in=True)

# Only logged-in users can access the route
@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-admin/dashboard_admin.html", name=current_user.name, logged_in=True)


@app.route("/klasifikasi_baru")
@login_required
def klasifikasi_baru():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-user/klasifikasi_baru.html", name=current_user.name, logged_in=True)

@app.route("/klasifikasi_admin")
@login_required
def klasifikasi_admin():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-admin/klasifikasi_admin.html", name=current_user.name, logged_in=True)


@app.route("/riwayat_klasifikasi")
@login_required
def riwayat_klasifikasi():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-user/riwayat_klasifikasi.html", name=current_user.name, logged_in=True)

@app.route("/riwayat_admin")
@login_required
def riwayat_admin():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-admin/riwayat_admin.html", name=current_user.name, logged_in=True)

@app.route("/profile")
@login_required
def profile():
    print(current_user.name)
    print(current_user.email)
    # Passing the name and email from the current_user
    return render_template("dashboard-user/profile.html", name=current_user.name, email=current_user.email, logged_in=True)

@app.route("/bantuan")
@login_required
def bantuan():
    print(current_user.name)
    # Passing the name from the current_user
    return render_template("dashboard-user/bantuan.html", name=current_user.name, logged_in=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)