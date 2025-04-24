from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import datetime
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleep-in.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB with the UserMixin
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    nama: Mapped[str] = mapped_column(String(100))
    jenis_kelamin: Mapped[str] = mapped_column(String(100))
    tanggal_lahir: Mapped[datetime.date] = mapped_column(String(100))
    no_telp: Mapped[str] = mapped_column(String(100))
    alamat: Mapped[str] = mapped_column(String(1000))
    kota: Mapped[str] = mapped_column(String(100))
    provinsi: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(1000))

class DataTraining(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jenis_kelamin: Mapped[str] = mapped_column(String(100))
    usia: Mapped[int] = mapped_column(Integer)
    durasi_tidur: Mapped[float] = mapped_column(Float)
    kualitas_tidur: Mapped[int] = mapped_column(Integer)
    tingkat_stres: Mapped[int] = mapped_column(Integer)
    detak_jantung: Mapped[int] = mapped_column(Integer)
    langkah_kaki: Mapped[int] = mapped_column(Integer)
    sistolik: Mapped[int] = mapped_column(Integer)
    diastolik: Mapped[int] = mapped_column(Integer)
    gangguan_tidur: Mapped[str] = mapped_column(String(100))

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
            nama=request.form.get('name'),
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
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-user/dashboard.html", name=current_user.nama, logged_in=True)

# Only logged-in users can access the route
@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-admin/dashboard_admin.html", name=current_user.nama, logged_in=True)


@app.route("/klasifikasi_baru")
@login_required
def klasifikasi_baru():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-user/klasifikasi_baru.html", name=current_user.nama, logged_in=True)

@app.route("/klasifikasi_admin")
@login_required
def klasifikasi_admin():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-admin/klasifikasi_admin.html", name=current_user.nama, logged_in=True)


@app.route("/riwayat_klasifikasi")
@login_required
def riwayat_klasifikasi():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-user/riwayat_klasifikasi.html", name=current_user.nama, logged_in=True)

@app.route("/riwayat_admin")
@login_required
def riwayat_admin():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-admin/riwayat_admin.html", name=current_user.nama, logged_in=True)

@app.route("/data_training")
@login_required
def data_training():
    print(current_user.nama)

    # Passing the name from the current_user
    return render_template("dashboard-admin/data_training.html", name=current_user.nama, logged_in=True)

@app.route("/data_training/upload", methods=["POST"])
@login_required
def upload_data_training():
    print("=== Mulai upload ===")

    if 'file' not in request.files:
        print("Tidak ada file dalam request.")
        flash("File tidak ditemukan dalam request.")
        return redirect(url_for("data_training"))

    file = request.files['file']
    print(f"Nama file: {file.filename}")

    if file.filename == '':
        print("File tidak dipilih.")
        flash("Tidak ada file yang dipilih.")
        return redirect(url_for("data_training"))

    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
            print("CSV berhasil dibaca")

            expected_columns = [
                'jenis_kelamin', 'usia', 'durasi_tidur', 'kualitas_tidur', 'tingkat_stres',
                'detak_jantung', 'langkah_kaki', 'sistolik', 'diastolik', 'gangguan_tidur'
            ]

            if not all(col in df.columns for col in expected_columns):
                print("Kolom tidak sesuai")
                flash("Kolom CSV tidak sesuai.")
                return redirect(url_for("data_training"))

            # Isi nilai NaN dengan string kosong atau default
            df = df.fillna({
                'gangguan_tidur': 'Tidak Diketahui'
            })

            for index, row in df.iterrows():
                try:
                    entry = DataTraining(
                        jenis_kelamin=str(row['jenis_kelamin']),
                        usia=int(row['usia']),
                        durasi_tidur=float(row['durasi_tidur']),
                        kualitas_tidur=int(row['kualitas_tidur']),
                        tingkat_stres=int(row['tingkat_stres']),
                        detak_jantung=int(row['detak_jantung']),
                        langkah_kaki=int(row['langkah_kaki']),
                        sistolik=int(row['sistolik']),
                        diastolik=int(row['diastolik']),
                        gangguan_tidur=str(row['gangguan_tidur']),
                    )
                    db.session.add(entry)
                except Exception as e:
                    print(f"Baris ke-{index} dilewati karena error: {e}")
                    continue  # lewati baris yang error

            db.session.commit()
            print("Commit berhasil")
            flash("Data berhasil diupload dan disimpan ke database.")

        except Exception as e:
            db.session.rollback()
            print(f"Error saat upload: {e}")
            flash(f"Terjadi kesalahan saat memproses file: {e}")

    else:
        print("File bukan CSV.")
        flash("Format file tidak didukung. Hanya CSV.")

    return redirect(url_for("data_training"))


@app.route("/manajemen_pengguna", methods=["GET"])
@login_required
def manajemen_pengguna():
    # Memeriksa apakah pengguna yang login adalah admin
    if current_user.role != "admin":
        flash("Anda tidak memiliki izin untuk mengakses halaman ini.", "error")
        return redirect(url_for("dashboard"))

    # Ambil semua user dari database
    users = User.query.all()

    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-admin/manajemen_pengguna.html",
                           name=current_user.nama,
                           users=users,
                           logged_in=True)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        nama_baru = request.form.get('nama')
        email_baru = request.form.get('email')
        jenis_kelamin_baru = request.form.get('jenis_kelamin')
        tanggal_lahir_baru = request.form.get('tanggal_lahir')
        no_telp_baru = request.form.get('no_telp')
        alamat_baru = request.form.get('alamat')
        kota_baru = request.form.get('kota')
        provinsi_baru = request.form.get('provinsi')

        # Cek apakah email baru sudah digunakan oleh pengguna lain
        if email_baru != current_user.email:
            result = db.session.execute(db.select(User).where(User.email == email_baru))
            existing_user = result.scalar()
            if existing_user:
                flash("Email sudah digunakan oleh pengguna lain.")
                return redirect(url_for('profile'))
            else:
                current_user.email = email_baru  # hanya update kalau email tidak konflik

        # Update data pengguna
        current_user.nama = nama_baru
        current_user.jenis_kelamin = jenis_kelamin_baru
        current_user.tanggal_lahir = tanggal_lahir_baru
        current_user.no_telp = no_telp_baru
        current_user.alamat = alamat_baru
        current_user.kota = kota_baru
        current_user.provinsi = provinsi_baru

        db.session.commit()
        flash("Profil berhasil diperbarui.")

        # Can redirect() and get name from the current_user
        return redirect(url_for("profile"))

    print(current_user.nama)
    print(current_user.email)
    print(current_user.jenis_kelamin)
    print(current_user.tanggal_lahir)
    print(current_user.no_telp)
    print(current_user.alamat)
    print(current_user.kota)
    print(current_user.provinsi)
    # Passing the name and email from the current_user
    return render_template("dashboard-user/profile.html",
                           name=current_user.nama,
                           nama=current_user.nama,
                           email=current_user.email,
                           jenis_kelamin=current_user.jenis_kelamin,
                           tanggal_lahir=current_user.tanggal_lahir,
                           no_telp=current_user.no_telp,
                           alamat=current_user.alamat,
                           kota=current_user.kota,
                           provinsi=current_user.provinsi,
                           logged_in=True)

@app.route("/pengaturan_sistem")
@login_required
def pengaturan_sistem():
    print(current_user.nama)
    print(current_user.email)
    # Passing the name from the current_user
    return render_template("dashboard-admin/pengaturan_sistem.html", name=current_user.nama, email=current_user.email, logged_in=True)


@app.route("/bantuan")
@login_required
def bantuan():
    print(current_user.nama)
    # Passing the name from the current_user
    return render_template("dashboard-user/bantuan.html", name=current_user.nama, logged_in=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
