from medicalApp.models import NguoiDung, DonViTinh, Thuoc, DanhSachLichKham, BenhNhanDatLich, UserRole, PhieuKham, \
    HoaDonThuoc, ChiTietHoaDon
from medicalApp import app, db
from sqlalchemy import func, extract
import hashlib
from flask_login import current_user


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def get_benh_nhan_by_HoTen(HoTen):
    # Truy vấn cơ sở dữ liệu để tìm bệnh nhân có HoTen tương ứng
    benhNhan = BenhNhanDatLich.query.filter_by(HoTen=HoTen).first()
    return benhNhan


def check_login(username, password, role=UserRole.BENHNHAN):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return NguoiDung.query.filter(NguoiDung.username.__eq__(username.strip()),
                                      NguoiDung.password.__eq__(password),
                                      NguoiDung.user_role.__eq__(role)).first()


def thuoc_count_by_cate():
    return DonViTinh.query.join(Thuoc, Thuoc.donViTinh_ID.__eq__(DonViTinh.id), isouter=True) \
        .add_columns(func.count(Thuoc.id)).group_by(DonViTinh.id).all()


def load_thuoc(kw=None, from_gia=None, to_gia=None):
    thuocs = Thuoc.query.all()

    if kw:
        thuocs = Thuoc.query.filter(Thuoc.tenThuoc.__contains__(kw))

    if from_gia:
        thuocs = Thuoc.query.filter(Thuoc.giaBan.__ge__(from_gia))

    if to_gia:
        thuocs = Thuoc.query.filter(Thuoc.giaBan.__ge__(to_gia))

    return thuocs


def load_danh_sach_lich_kham():
    return DanhSachLichKham.query.all()


def load_benh_nhan_kham(dslk_id=None):
    dsbnk = BenhNhanDatLich.query.all()

    if dslk_id:
        dsbnk = BenhNhanDatLich.query.filter(BenhNhanDatLich.danhSachLichKham_id.__eq__(dslk_id))

    return dsbnk


def add_user(name, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = NguoiDung(Ten=name.strip(),
                     username=username.strip(),
                     password=password)

    db.session.add(user)
    db.session.commit()


def check_so_luong_kham(id1):
    patient_count = db.session.query(func.count(BenhNhanDatLich.id)). \
        join(DanhSachLichKham, BenhNhanDatLich.danhSachLichKham_id == DanhSachLichKham.id). \
        filter(DanhSachLichKham.id == id1).scalar()

    return patient_count


def add_lich_kham(hoTen, gioiTinh, namSinh, diaChi, SDT, nguoiDung_id, lk_id):
    benhNhan = BenhNhanDatLich(HoTen=hoTen,
                               gioiTinh=gioiTinh,
                               namSinh=namSinh,
                               diaChi=diaChi,
                               SDT=SDT,
                               nguoiDung_id=nguoiDung_id,
                               danhSachLichKham_id=lk_id)

    db.session.add(benhNhan)
    db.session.commit()


def create_one_schedule(ngayTaoLich):
    lichKham = DanhSachLichKham(NgayTao=ngayTaoLich)

    db.session.add(lichKham)
    db.session.commit()


def tinh_tien_thuoc():
    # Sử dụng func.sum để tính tổng tiền cho mỗi chi tiết đơn thuốc
    ket_qua = (ChiTietHoaDon.query
               .join(Thuoc, Thuoc.id == ChiTietHoaDon.thuoc_id)
               .join(PhieuKham, PhieuKham.id == ChiTietHoaDon.phieuKham_id)
               .join(BenhNhanDatLich, BenhNhanDatLich.nguoiDung_id == PhieuKham.nguoiDung_id)
               .with_entities(
        PhieuKham.id.label('phieuKham_id'),  # Đổi tên cột cho rõ ràng
        PhieuKham.ngayKham.label('ngayKham'),
        BenhNhanDatLich.HoTen.label('HoTen'),
        func.sum(Thuoc.giaBan * ChiTietHoaDon.soLuong).label('tongTien')
    )
               .group_by(PhieuKham.id, PhieuKham.ngayKham, BenhNhanDatLich.HoTen)  # Group theo các trường tương ứng
               .all())

    return ket_qua


def add_hoa_don(tienThuoc, phieuKham_id):
    hoaDon = HoaDonThuoc(tienThuoc=tienThuoc,
                         phieuKham_id=phieuKham_id)

    db.session.add(hoaDon)
    db.session.commit()


def load_hoa_don():
    return HoaDonThuoc.query.all()


def load_ds_hoa_don(hoTen=None):
    # danh_sach_tong_tien = tinh_tien_thuoc()
    #
    # for phieuKham_id, ngayKham, HoTen, tienThuoc in danh_sach_tong_tien:
    #     add_hoa_don(tienThuoc=tienThuoc, trangThai=True, phieuKham_id=phieuKham_id)

    ket_qua = (HoaDonThuoc.query
               .join(PhieuKham, PhieuKham.id == HoaDonThuoc.phieuKham_id)
               .join(BenhNhanDatLich, BenhNhanDatLich.nguoiDung_id == PhieuKham.nguoiDung_id)
               .with_entities(
        HoaDonThuoc.id.label('hoaDon_id'),  # Đổi tên cột cho rõ ràng
        BenhNhanDatLich.HoTen.label('hoTen'),
        PhieuKham.ngayKham.label('ngayKham'),
        HoaDonThuoc.tienKham.label('tienKham'),
        HoaDonThuoc.tienThuoc.label('tienThuoc'),
        HoaDonThuoc.trangThai.label('trangThai'),
    ).all())

    if hoTen:
        ket_qua = (HoaDonThuoc.query
                   .join(PhieuKham, PhieuKham.id == HoaDonThuoc.phieuKham_id)
                   .join(BenhNhanDatLich, BenhNhanDatLich.nguoiDung_id == PhieuKham.nguoiDung_id)
                   .filter(BenhNhanDatLich.HoTen.contains(hoTen))
                   .with_entities(
            HoaDonThuoc.id.label('hoaDon_id'),  # Đổi tên cột cho rõ ràng
            BenhNhanDatLich.HoTen.label('hoTen'),
            PhieuKham.ngayKham.label('ngayKham'),
            HoaDonThuoc.tienKham.label('tienKham'),
            HoaDonThuoc.tienThuoc.label('tienThuoc'),
            HoaDonThuoc.trangThai.label('trangThai'),
        ).all())

    return ket_qua


def thong_ke_01(thang=None):
    ket_qua = (HoaDonThuoc.query
               .join(PhieuKham, PhieuKham.id == HoaDonThuoc.phieuKham_id)
               .join(BenhNhanDatLich, BenhNhanDatLich.nguoiDung_id == PhieuKham.nguoiDung_id)
               .join(DanhSachLichKham, DanhSachLichKham.id == BenhNhanDatLich.danhSachLichKham_id)
               .with_entities(
        # Đổi tên cột cho rõ ràng
        func.date(PhieuKham.ngayKham).label('ngayKham'),
        func.count(BenhNhanDatLich.id).label('SoBenhNhan'),
        func.sum(HoaDonThuoc.tienThuoc + HoaDonThuoc.tienKham).label('doanhThu'),
    ).group_by(PhieuKham.ngayKham).all())

    if thang:
        ket_qua = (HoaDonThuoc.query
                   .join(PhieuKham, PhieuKham.id == HoaDonThuoc.phieuKham_id)
                   .join(BenhNhanDatLich, BenhNhanDatLich.nguoiDung_id == PhieuKham.nguoiDung_id)
                   .join(DanhSachLichKham, DanhSachLichKham.id == BenhNhanDatLich.danhSachLichKham_id)
                   .filter(func.extract('month', PhieuKham.ngayKham) == thang)
                   .with_entities(
            # Đổi tên cột cho rõ ràng
            func.date(PhieuKham.ngayKham).label('ngayKham'),
            func.count(BenhNhanDatLich.id).label('SoBenhNhan'),
            func.sum(HoaDonThuoc.tienThuoc + HoaDonThuoc.tienKham).label('doanhThu'),
        ).group_by(PhieuKham.ngayKham).all())

    return ket_qua


def thong_ke_02(thang=None):
    result = db.session.query(
        Thuoc.id.label('thuoc_id'),
        Thuoc.tenThuoc.label('tenThuoc'),
        DonViTinh.tenDonViTinh.label('tenDonViTinh'),
        func.sum(Thuoc.soLuong).label('soLuongThuoc'),
        func.count(ChiTietHoaDon.id).label('soLanDung')  # Đếm số lần xuất hiện của mỗi thuốc
    ).join(
        Thuoc, ChiTietHoaDon.thuoc_id == Thuoc.id
    ).join(
        DonViTinh, Thuoc.donViTinh_ID == DonViTinh.id
    ).group_by(
        ChiTietHoaDon.thuoc_id, Thuoc.tenThuoc, DonViTinh.tenDonViTinh
    ).all()

    if thang:
        result = (db.session.query(
            Thuoc.id.label('thuoc_id'),
            Thuoc.tenThuoc.label('tenThuoc'),
            DonViTinh.tenDonViTinh.label('tenDonViTinh'),
            func.sum(Thuoc.soLuong).label('soLuongThuoc'),
            func.count(ChiTietHoaDon.id).label('soLanDung')  # Đếm số lần xuất hiện của mỗi thuốc
        ).join(
            Thuoc, ChiTietHoaDon.thuoc_id == Thuoc.id
        ).join(
            DonViTinh, Thuoc.donViTinh_ID == DonViTinh.id
        ).join(PhieuKham, PhieuKham.id == ChiTietHoaDon.phieuKham_id
               ).filter(func.extract('month', PhieuKham.ngayKham) == thang)
                  ).group_by(
            ChiTietHoaDon.thuoc_id, Thuoc.tenThuoc, DonViTinh.tenDonViTinh, PhieuKham.ngayKham
        ).all()

    return result


def ngay_kham_of_user(user_id):
    ket_qua = (db.session.query(
        BenhNhanDatLich.nguoiDung_id.label('nguoiDung_id'),
        DanhSachLichKham.NgayTao.label('ngayDangKyKham')
    ).join(
        BenhNhanDatLich, BenhNhanDatLich.danhSachLichKham_id == DanhSachLichKham.id
    ).filter(BenhNhanDatLich.nguoiDung_id == user_id)
               ).all()

    return ket_qua


def add_phieu_kham(trieuChung=None, chuanDoan=None, bacSy=None, nguoiDung_id=None):
    phieuKham = PhieuKham(trieuChung=trieuChung,
                          duDoanLoaiBenh=chuanDoan,
                          bacSy=bacSy,
                          nguoiDung_id=nguoiDung_id)

    db.session.add(phieuKham)
    db.session.commit()


def get_nguoidung_ids_from_benh_nhan_dat_lich():
    # Sử dụng session của bạn (ví dụ: db.session) để truy vấn
    results = BenhNhanDatLich.query.with_entities(BenhNhanDatLich.nguoiDung_id).all()

    return results


def list_thuoc():
    ket_qua = (db.session.query(
        Thuoc.id.label('thuoc_id'),
        Thuoc.tenThuoc.label('tenThuoc'),
        DonViTinh.tenDonViTinh.label('tenDonViTinh'),
        Thuoc.giaBan.label('giaBan')
    ).join(
        Thuoc, Thuoc.donViTinh_ID == DonViTinh.id
    )
    ).all()

    return ket_qua


def count_thuoc_of_toa_thuoc(toaThuoc):
    totalThuocQuantity = 0
    total_amount = 0

    if toaThuoc:
        for tt in toaThuoc.values():
            totalThuocQuantity += tt['soLuong']
            total_amount += tt['soLuong'] * tt['giaBan']

    return {
        'totalThuocQuantity': totalThuocQuantity,
        'total_amount': total_amount
    }


def add_chitiethoadon(toaThuoc, phieuKham_id):
    if toaThuoc:
        for tt in toaThuoc.values():
            cthd = ChiTietHoaDon(soLuong=tt['soLuong'],
                                 thuoc_id=tt['id'],
                                 phieuKham_id=phieuKham_id)
            db.session.add(cthd)
        db.session.commit()


def load_phieu_kham():
    return PhieuKham.query.all()
