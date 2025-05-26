from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import UserMixin, LoginManager
from datetime import datetime
import pytz

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

wib = pytz.timezone('Asia/Jakarta')
now_wib = datetime.now(wib)

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
    role: Mapped[str] = mapped_column(String(100))

class DataTraining(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jenis_kelamin: Mapped[str] = mapped_column(String(100))
    usia: Mapped[int] = mapped_column(Integer)
    durasi_tidur: Mapped[float] = mapped_column(Float)
    kualitas_tidur: Mapped[int] = mapped_column(Integer)
    tingkat_stres: Mapped[int] = mapped_column(Integer)
    kategori_bmi: Mapped[str] = mapped_column(String(100))
    denyut_jantung: Mapped[int] = mapped_column(Integer)
    langkah_harian: Mapped[int] = mapped_column(Integer)
    sistolik: Mapped[int] = mapped_column(Integer)
    diastolik: Mapped[int] = mapped_column(Integer)
    gangguan_tidur: Mapped[str] = mapped_column(String(100))

class HasilKlasifikasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    waktu = db.Column(db.DateTime, default=datetime.utcnow)
    nama = db.Column(db.String(100))
    hasil = db.Column(db.String(100))