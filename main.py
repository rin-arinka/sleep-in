from flask import Flask, render_template, request, url_for, redirect, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from models import db, User, DataTraining, HasilKlasifikasi, now_wib
from knn import predict_sleep_disorder,train_and_save_knn_model
from sqlalchemy import func, asc
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleep-in.db'
db.init_app(app)

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

        # Mencari user berdasarkan email yang dimasukkan.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # Email tidak terdaftar atau password salah.
        if not user:
            flash("Email tidak terdaftar, silahkan daftar terlebih dahulu.")
            return redirect(url_for('login'))
        # Mengecek kata sandi yang dimasukkan dengan yang tersimpan di database.
        elif not check_password_hash(user.password, password):
            flash('Password salah, silahkan coba lagi.')
            return redirect(url_for('login'))
        else:
            login_user(user)

            #Mengecek role user atau admin.
            if user.role == 'admin':
                return redirect(url_for('dashboard_admin'))

            else:
                return redirect(url_for('dashboard'))

    return render_template("authentications/login.html", logged_in=current_user.is_authenticated)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # User sudah terdaftar
            flash("Email sudah terdaftar, silahkan login.")
            return redirect(url_for('sign_up'))

        # Hashing dan salting password yang dimasukkan pengguna
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Menyimpan data ke dalam database tabel user
        new_user = User(
            email=request.form.get('email'),
            nama=request.form.get('name'),
            password=hash_and_salted_password,
            role='user',
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        # Mengarahkan ke halaman dashboard
        return redirect(url_for("dashboard"))

    return render_template("authentications/sign_up.html", logged_in=current_user.is_authenticated)

# Hanya pengguna yang sudah login yang dapat mengakses halaman
@app.route('/dashboard')
@login_required
def dashboard():
    hasil_terakhir = HasilKlasifikasi.query.filter_by(user_id=current_user.id).order_by(HasilKlasifikasi.waktu.desc()).first()
    riwayat = HasilKlasifikasi.query.filter_by(user_id=current_user.id).order_by(HasilKlasifikasi.waktu.desc()).limit(10).all()

    # Passing the name from the current_user
    return render_template("dashboard-user/dashboard.html", name=current_user.nama,
                           hasil_terakhir=hasil_terakhir, riwayat=riwayat, logged_in=True)

@app.route("/klasifikasi_baru")
@login_required
def klasifikasi_baru():

    return render_template("dashboard-user/klasifikasi_baru.html", name=current_user.nama, logged_in=True)

@app.route("/klasifikasi_gangguan", methods=["POST"])
@login_required
def klasifikasi_gangguan():
    # Ambil input data dari request JSON
    input_data = request.json

    # Klasifikasi gangguan tidur
    try:
        hasil_klasifikasi = predict_sleep_disorder(input_data)

        # Simpan hasil ke database
        hasil = HasilKlasifikasi(
            waktu=now_wib,
            nama=current_user.nama,
            hasil=hasil_klasifikasi,
            user_id=current_user.id  # <-- ini wajib ditambahkan
         )
        db.session.add(hasil)
        db.session.commit()

        return jsonify({
            "hasil_klasifikasi": hasil_klasifikasi,
            "status": "success"
        })

    except Exception as e:
        print(f"❗ Error klasifikasi: {e}")  # Tambahkan ini untuk debug
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route("/riwayat_klasifikasi",methods=["GET"])
@login_required
def riwayat_klasifikasi():

    riwayat = (HasilKlasifikasi.query
               .filter_by(user_id=current_user.id)  # Filter by user ID
               .order_by(HasilKlasifikasi.waktu.desc())
               .limit(10)
               .all())

    return render_template("dashboard-user/riwayat_klasifikasi.html",
                           name=current_user.nama, riwayat_prediksi=riwayat, logged_in=True)

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

        return redirect(url_for("profile"))

    return render_template("dashboard-user/profile.html", name=current_user.nama,
                           nama=current_user.nama, email=current_user.email,
                           jenis_kelamin=current_user.jenis_kelamin, tanggal_lahir=current_user.tanggal_lahir,
                           no_telp=current_user.no_telp, alamat=current_user.alamat,
                           kota=current_user.kota, provinsi=current_user.provinsi, logged_in=True)

@app.route("/bantuan")
@login_required
def bantuan():

    return render_template("dashboard-user/bantuan.html", name=current_user.nama, logged_in=True)

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    total_pengguna = User.query.count()
    total_klasifikasi = HasilKlasifikasi.query.count()
    total_data_training = DataTraining.query.count()

    # Ambil jumlah hasil klasifikasi per jenis gangguan
    hasil_statistik = (
        db.session.query(HasilKlasifikasi.hasil, func.count(HasilKlasifikasi.hasil))
        .group_by(HasilKlasifikasi.hasil)
        .all()
    )

    # Bagi hasil ke dalam dua list untuk label dan data
    label_gangguan = [item[0] for item in hasil_statistik]
    jumlah_gangguan = [item[1] for item in hasil_statistik]

    return render_template("dashboard-admin/dashboard_admin.html",
                           name=current_user.nama, total_pengguna=total_pengguna,
                           total_klasifikasi=total_klasifikasi, total_data_training=total_data_training,
                           label_gangguan=label_gangguan, jumlah_gangguan=jumlah_gangguan, logged_in=True)

@app.route("/klasifikasi_admin")
@login_required
def klasifikasi_admin():
    users = User.query.order_by(asc(User.nama)).all()  # Urutkan berdasarkan abjad A-Z

    return render_template("dashboard-admin/klasifikasi_admin.html",
                           name=current_user.nama, users=users, logged_in=True)

@app.route("/riwayat_admin")
@login_required
def riwayat_admin():

    riwayat = HasilKlasifikasi.query.order_by(HasilKlasifikasi.waktu.desc()).limit(10).all()

    return render_template("dashboard-admin/riwayat_admin.html",
                           name=current_user.nama, riwayat_prediksi=riwayat,
                           logged_in=True)

@app.route("/data_training", methods=["GET"])
@login_required
def data_training():
    # Memeriksa apakah pengguna yang login adalah admin
    if current_user.role != "admin":
        flash("Anda tidak memiliki izin untuk mengakses halaman ini.", "error")
        return redirect(url_for("dashboard"))

    # Ambil parameter halaman dari URL (default ke halaman 1)
    page = request.args.get("page", 1, type=int)
    per_page = 10  # jumlah data per halaman

    # Gunakan paginate untuk membatasi data yang ditampilkan
    data_training_paginated = DataTraining.query.paginate(page=page, per_page=per_page)

    return render_template("dashboard-admin/data_training.html",
                           name=current_user.nama, data_training=data_training_paginated.items,
                           pagination=data_training_paginated, logged_in=True)

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
                "Jenis Kelamin", "Usia", "Durasi Tidur", "Kualitas Tidur", "Tingkat Stres",
                "Kategori BMI", "Denyut Jantung", "Langkah Harian", "Sistolik", "Diastolik", "Gangguan Tidur"
            ]

            if not all(col in df.columns for col in expected_columns):
                print("Kolom tidak sesuai")
                flash("Kolom CSV tidak sesuai.")
                return redirect(url_for("data_training"))

            # Isi nilai NaN dengan string kosong atau default
            df = df.fillna({
                'Gangguan Tidur': 'Normal'
            })

            for index, row in df.iterrows():
                try:
                    entry = DataTraining(
                        jenis_kelamin=str(row['Jenis Kelamin']),
                        usia=int(row['Usia']),
                        durasi_tidur=float(row['Durasi Tidur']),
                        kualitas_tidur=int(row['Kualitas Tidur']),
                        tingkat_stres=int(row['Tingkat Stres']),
                        kategori_bmi=str(row['Kategori BMI']),
                        denyut_jantung=int(row['Denyut Jantung']),
                        langkah_harian=int(row['Langkah Harian']),
                        sistolik=int(row['Sistolik']),
                        diastolik=int(row['Diastolik']),
                        gangguan_tidur=str(row['Gangguan Tidur']),
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

@app.route("/train_knn", methods=["GET"])
@login_required
def train_knn():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    result = train_and_save_knn_model()
    return jsonify({"message": result})

@app.route("/manajemen_pengguna", methods=["GET", "POST"])
@login_required
def manajemen_pengguna():
    # Memeriksa apakah pengguna yang login adalah admin
    if current_user.role != "admin":
        flash("Anda tidak memiliki izin untuk mengakses halaman ini.", "error")
        return redirect(url_for("dashboard"))

    # Ambil parameter halaman dari URL (default ke halaman 1)
    page = request.args.get("page", 1, type=int)
    per_page = 10  # jumlah data per halaman

    # Gunakan paginate untuk membatasi data yang ditampilkan
    user_paginated = User.query.paginate(page=page, per_page=per_page)

    if request.method == "POST":
        email = request.form.get('email')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # User sudah terdaftar
            flash("Email sudah terdaftar")
            return redirect(url_for('manajemen_pengguna'))

        # Hashing dan salting password yang dimasukkan pengguna
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Menyimpan data ke dalam database tabel user
        new_user = User(
            nama=request.form.get('nama'),
            email=request.form.get('email'),
            password=hash_and_salted_password,
            role=request.form.get('role'),
            jenis_kelamin=request.form.get('jenis_kelamin'),
            tanggal_lahir=request.form.get('tanggal_lahir'),
            no_telp=request.form.get('no_telp'),
            alamat=request.form.get('alamat'),
            kota=request.form.get('kota'),
            provinsi=request.form.get('provinsi'),

        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("manajemen_pengguna"))
    return render_template("dashboard-admin/manajemen_pengguna.html",
                           name=current_user.nama, user=user_paginated.items,
                           pagination=user_paginated, logged_in=True)

@app.route("/profile_admin", methods=["GET", "POST"])
@login_required
def profile_admin():
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

        return redirect(url_for("profile_admin"))

    return render_template("dashboard-admin/profile_admin.html", name=current_user.nama,
                           nama=current_user.nama, email=current_user.email,
                           jenis_kelamin=current_user.jenis_kelamin, tanggal_lahir=current_user.tanggal_lahir,
                           no_telp=current_user.no_telp, alamat=current_user.alamat,
                           kota=current_user.kota, provinsi=current_user.provinsi, logged_in=True)


@app.route("/pengaturan_sistem")
@login_required
def pengaturan_sistem():
    print(current_user.nama)
    print(current_user.email)
    # Passing the name from the current_user
    return render_template("dashboard-admin/pengaturan_sistem.html", name=current_user.nama, email=current_user.email, logged_in=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
