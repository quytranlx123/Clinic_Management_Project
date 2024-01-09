from medicalApp import db, app, utils
from medicalApp.models import NguoiDung, PhieuKham, Thuoc, ChiTietHoaDon, HoaDonThuoc, DonViTinh, BenhNhanDatLich, \
    DanhSachLichKham, UserRole
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_login import logout_user, current_user
from flask import redirect, request, url_for


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.QUANTRI


class NguoiDungView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    # column_filters = ['id', 'nguoiDung_id']
    column_labels = {
        'id': 'Mã người dùng',
        'Ten': 'Tên',
        'ngayTao': 'Ngày tạo',
        'user_role': 'Phân quyền'
    }


class PhieuKhamView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    column_list = ['id', 'ngayKham', 'trieuChung', 'duDoanLoaiBenh', 'bacSy', 'nguoiDung_id']
    # column_exclude_list = ['image']
    column_filters = ['id', 'nguoiDung_id', 'ngayKham']
    # column_searchable_list = ['name', 'description']
    column_labels = {
        'id': 'Mã phiếu khám',
        'ngayKham': 'Ngày khám',
        'trieuChung': 'Triệu chứng',
        'duDoanLoaiBenh': 'Dự đoán loại bệnh',
        'tienKham': 'Tiền khám',
        'bacSy': 'Bác sỹ',
        'nguoiDung_id': 'Mã bệnh nhân',
    }
    # form_excluded_columns = ['tags']


class ThuocView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    column_list = ['id', 'tenThuoc', 'moTa', 'giaBan', 'soLuong', 'donViTinh_ID']
    column_filters = ['id', 'tenThuoc', 'donViTinh_ID']
    column_labels = {
        'id': 'Mã thuốc',
        'tenThuoc': 'Tên thuốc',
        'moTa': 'Mô tả',
        'giaBan': 'Giá bán',
        'soLuong': 'Số lượng',
        'donViTinh_ID': 'Đơn vị tính'
    }


class ChiTietHoaDonView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    column_list = ['id', 'soLuong', 'thuoc_id', 'phieuKham_id']
    column_filters = ['id', 'phieuKham_id']
    column_labels = {
        'id': 'Mã chi tiết hóa đơn',
        'soLuong': 'Số lượng',
        'thuoc_id': 'Mã thuốc',
        'phieuKham_id': 'Mã phiếu khám'
    }


class HoaDonThuocView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    column_list = ['id', 'ngayLapPhieu', 'tienKham', 'tienThuoc', 'phieuKham_id']
    column_filters = ['id', 'phieuKham_id']
    column_labels = {
        'id': 'Mã hóa đơn thuốc',
        'ngayLapPhieu': 'Ngày lập phiếu',
        'tienKham': 'Tiền Khám',
        'tienThuoc': 'Tiền thuốc',
        'trangThai': 'Trạng thái',
        'phieuKham_id': 'Mã phiếu khám'
    }


class DonViTinhView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    # column_filters = ['id', 'nguoiDung_id']
    column_labels = {
        'id': 'Mã đơn vị tính',
        'tenDonViTinh': 'Tên đơn vị tính',
    }


class BenhNhanDatLichView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    column_list = ['id', 'HoTen', 'gioiTinh', 'namSinh', 'diaChi', 'SDT', 'nguoiDung_id', 'danhSachLichKham_id']
    column_filters = ['id', 'nguoiDung_id', 'HoTen', 'danhSachLichKham_id']
    column_labels = {
        'id': 'Mã đặt lịch',
        'HoTen': 'Họ và tên',
        'gioiTinh': 'Giới tính',
        'namSinh': 'Năm sinh',
        'diaChi': 'Địa chỉ',
        'SDT': 'SĐT',
        'nguoiDung_id': 'Mã bệnh nhân',
        'danhSachLichKham_id': 'Mã danh sách khám'
    }


class DanhSachLichKhamView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True
    # column_filters = ['id', 'nguoiDung_id']
    column_labels = {
        'id': 'Mã danh sách lịch khám',
        'NgayTao': 'Ngày tạo',
    }


class logoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('user_signin'))

    def is_accessible(self):
        return current_user.is_authenticated


class statsView(BaseView):
    @expose('/')
    def index(self):
        tongDoanhThu = 0
        tongBenhNhan = 0
        thang = request.args.get('thang01')
        thang02 = request.args.get('thang02')
        thong_ke_01 = utils.thong_ke_01(thang)
        thong_ke_02 = utils.thong_ke_02(thang02)
        for row in thong_ke_01:
            tongDoanhThu += row.doanhThu
            tongBenhNhan += row.SoBenhNhan

        return self.render('admin/stats.html', thong_ke_01=thong_ke_01, thong_ke_02=thong_ke_02,
                           tongDoanhThu=tongDoanhThu, tongBenhNhan=tongBenhNhan)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.QUANTRI


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = utils.thuoc_count_by_cate()
        return self.render('admin/index.html', stats=stats)


admin = Admin(app=app,
              name='PHÒNG MẠCH QHN',
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())
admin.add_view(NguoiDungView(NguoiDung, db.session, name='Người dùng'))
admin.add_view(PhieuKhamView(PhieuKham, db.session, name='Phiếu khám'))
admin.add_view(ThuocView(Thuoc, db.session, name='Thuốc'))
admin.add_view(ChiTietHoaDonView(ChiTietHoaDon, db.session, name='Chi tiết hóa đơn'))
admin.add_view(HoaDonThuocView(HoaDonThuoc, db.session, name='Hóa đơn thuốc'))
admin.add_view(DonViTinhView(DonViTinh, db.session, name='Đơn vị tính'))
admin.add_view(BenhNhanDatLichView(BenhNhanDatLich, db.session, name='Bệnh nhân đặt lịch'))
admin.add_view(DanhSachLichKhamView(DanhSachLichKham, db.session, name='Danh sách lịch khám'))
admin.add_view(statsView(name='Thống kê báo cáo'))
admin.add_view(logoutView(name='Đăng xuất'))
