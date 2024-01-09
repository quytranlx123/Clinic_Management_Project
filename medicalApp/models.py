from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Date
from sqlalchemy.orm import relationship, backref
from medicalApp import db, app
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin, login_manager, LoginManager


class UserRole(UserEnum):
    QUANTRI = 1
    BENHNHAN = 2
    YTA = 3
    BACSY = 4


class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'NguoiDung'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Ten = Column(String(40), nullable=False)
    ngayTao = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.BENHNHAN)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    benhNhanDatLichs = relationship('BenhNhanDatLich', backref='NguoDung', lazy=True)
    phieuKhams = relationship('PhieuKham', backref='NguoiDung', lazy=False)

    def __str__(self):
        return self.name

    # def __init__(self, user_id):
    #     self.id = user_id


class DanhSachLichKham(db.Model):
    __tablename__ = 'DanhSachLichKham'
    id = Column(Integer, primary_key=True, autoincrement=True)
    NgayTao = Column(Date, default=datetime.now().date())
    benhNhanDatLichs = relationship('BenhNhanDatLich', backref='DanhSachLichKham', lazy=False)

    def __str__(self):
        return self.name


class BenhNhanDatLich(db.Model):
    __tablename__ = 'BenhNhanDatLich'
    id = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(40), nullable=False)
    gioiTinh = Column(String(10), nullable=False)
    namSinh = Column(Date, default=datetime.now().date(), nullable=False)
    diaChi = Column(String(50), nullable=False)
    SDT = Column(String(10), nullable=False)
    nguoiDung_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=False)
    danhSachLichKham_id = Column(Integer, ForeignKey('DanhSachLichKham.id'), nullable=False)

    def __str__(self):
        return self.name


class PhieuKham(db.Model):
    __tablename__ = 'PhieuKham'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngayKham = Column(Date, default=datetime.now().date())
    trieuChung = Column(String(100), nullable=False)
    duDoanLoaiBenh = Column(String(50), nullable=False)
    # tienKham = Column(Float, default=0)
    bacSy = Column(String(40), nullable=False)
    nguoiDung_id = Column(Integer, ForeignKey('NguoiDung.id'), nullable=False)
    hoaDonThuoc = relationship('HoaDonThuoc', backref='PhieuKham', uselist=False)
    chiTietHoaDons = relationship('ChiTietHoaDon', backref='PhieuKham')

    def __str__(self):
        return self.name


class Thuoc(db.Model):
    __tablename__ = 'Thuoc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenThuoc = Column(String(50), nullable=False)
    moTa = Column(String(255))
    giaBan = Column(Float, default=0)
    soLuong = Column(Integer, default=0)
    donViTinh_ID = Column(Integer, ForeignKey('DonViTinh.id'), nullable=False)
    chiTietHoaDons = relationship('ChiTietHoaDon', backref='Thuoc')

    def __str__(self):
        return self.name


class DonViTinh(db.Model):
    __tablename__ = 'DonViTinh'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenDonViTinh = Column(String(10), nullable=False, unique=True)
    thuocs = relationship('Thuoc', backref='Donvitinh', lazy=True)

    def __str__(self):
        return self.name


class ChiTietHoaDon(db.Model):
    __tablename__ = 'ChiTietHoaDon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    soLuong = Column(Integer, default=0)
    thuoc_id = Column(ForeignKey('Thuoc.id'), primary_key=True)
    phieuKham_id = Column(ForeignKey('PhieuKham.id'), primary_key=True)

    def __str__(self):
        return self.name


class HoaDonThuoc(db.Model):
    __tablename__ = 'HoaDonThuoc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngayLapPhieu = Column(Date, default=datetime.now().date())
    tienKham = Column(Float, default=100000)
    tienThuoc = Column(Float, default=0)
    trangThai = Column(Boolean, default=False)
    phieuKham_id = Column(Integer, ForeignKey('PhieuKham.id'), nullable=False)

    def __str__(self):
        return self.name


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

