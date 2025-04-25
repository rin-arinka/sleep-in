from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import UserMixin, LoginManager
import datetime

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


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
