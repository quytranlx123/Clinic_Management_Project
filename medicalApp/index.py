from flask import render_template, request, redirect, url_for, session, jsonify
from medicalApp import app, login, LoginManager
import os
import utils
from medicalApp.admin import *
from flask_login import login_user, logout_user, current_user, UserMixin, login_required, login_manager
from medicalApp.models import UserRole
from flask import session
from datetime import datetime, date


# @app.route("/")
# def home():
#     users = [{
#         "name": "Nguyen Van A",
#         "email": "a@gamil.com"
#     }, {
#         "name": "Tran Thi B",
#         "email": "b@gamil.com"
#     }, {
#         "name": "Vo Van C",
#         "email": "c@gamil.com"
#     }]
#
#     kw = request.args.get("keyword")
#
#     if kw:
#         # users = [u for u in users if u['name'].find(kw) >= 0] biểu thức viết gọn
#         kq = []
#
#         for u in users:
#             if u['name'].lower().find(kw.lower()) >= 0:
#                 kq.append(u)
#
#         users = kq
#
#
#     return render_template('index.html', users = users)

# @app.route("/id")
# def id():
#     return render_template('index.html')
#
# #path params
# @app.route("/hello/<int:name>")
# def hello(name):
#     return render_template('index.html', message = "XIN CHAO %s!!" % name)
#
# #get params
# @app.route("/hello")
# def hello2():
#     fn = request.args.get('first_name', 'A')
#     ln = request.args.get('last_name', 'B')
#     return render_template('index.html', message = "XIN CHAO %s %s!!" % (fn, ln))
#
# @app.route("/login", methods = ['post'])
# def login():
#     username = request.form['username']
#     password = request.form['password']
#
#     if username == "admin" and password == "123":
#         return 'successful'
#
#     return 'failed'
#
# @app.route("/upload", methods = ['post'])
# def upload():
#     f = request.files['avatar']
#
#     f.save(os.path.join(app.root_path, 'static/uploads/', f.filename))
#
#     return 'DONE.'

def get_date_only():
    # Lấy ngày hiện tại
    current_datetime = datetime.now()
    # date_only = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    date_only = current_datetime.date()
    # Chỉ lấy giá trị ngày, tháng và năm
    date_only = current_datetime.strftime('%Y-%m-%d')


@app.context_processor
def common_response():
    return {
        'thuoc_stats': utils.count_thuoc_of_toa_thuoc(session.get('toaThuoc'))
    }


@app.route("/")
def home():
    stats = utils.thuoc_count_by_cate()
    return render_template("index.html", stats=stats)


@app.route("/admin-login", methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password, role=UserRole.QUANTRI)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/yta-login", methods=['post'])
def yta_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password, role=UserRole.YTA)
    if user:
        login_user(user=user)

    return redirect('/home')


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route("/dslk")
def load_dslk():
    dslk = utils.load_danh_sach_lich_kham()

    dslk_id = request.args.get('danhSachLichKham_id')
    dsbn = utils.load_benh_nhan_kham(dslk_id=dslk_id)
    return render_template("load_dslk.html", dslk=dslk, dsbn=dsbn)


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm')

        try:
            if password.strip().__eq__(confirmPassword.strip()):
                utils.add_user(name=name, username=username, password=password)
                return redirect(url_for('user_signin'))
            else:
                err_msg = "Xác nhận mật khẩu không đúng!!"
        except Exception as ex:
            err_msg = "Hệ thống đang có lỗi" + str(ex)

    return render_template("register.html", err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            session['user_id'] = user.id
            return redirect(url_for('home'))

        user = utils.check_login(username=username, password=password, role=UserRole.YTA)
        if user:
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('home'))

        # If not YTA, try as BACSY
        user = utils.check_login(username=username, password=password, role=UserRole.BACSY)
        if user:
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('home'))

        user = utils.check_login(username=username, password=password, role=UserRole.QUANTRI)
        if user:
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for('admin.index'))

        err_msg = "Username hoặc Password không chính xác, vui lòng thử lại"

    return render_template('login.html', err_msg=err_msg)


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/book-form', methods=['GET', 'POST'])
@login_required
def book_form():
    err_msg = ""
    dslk = utils.load_danh_sach_lich_kham()
    nguoiDung_id = session.get('user_id')
    if request.method == 'POST':
        hoTen = request.form.get('hoTen')
        gioiTinh = request.form.get('gioiTinh')
        namSinh = request.form.get('namSinh')
        diaChi = request.form.get('diaChi')
        SDT = request.form.get('SDT')
        lk_id = request.form.get('dslk')

        soLuongBenhNhan = utils.check_so_luong_kham(lk_id)

        if soLuongBenhNhan < 40:
            utils.add_lich_kham(hoTen=hoTen, gioiTinh=gioiTinh, namSinh=namSinh, diaChi=diaChi, SDT=SDT
                                , nguoiDung_id=nguoiDung_id, lk_id=lk_id)
            return render_template('book_form.html', soLuongBenhNhan=soLuongBenhNhan, lk_id=lk_id)
        else:
            err_msg = "Danh sách khám này đã đầy"

    return render_template('book_form.html', dslk=dslk, err_msg=err_msg)


@app.route('/create-schedule', methods=['GET', 'POST'])
@login_required
def create_schedule():
    err_msg = ""
    dslk = utils.load_danh_sach_lich_kham()
    flat = True
    if request.method == 'POST':
        # ngayTaoLich = request.form.get('ngayTaolich')
        ngayTaoLich_str = request.form.get('ngayTaolich')  # Lấy chuỗi ngày từ form
        ngayTaoLich = datetime.strptime(ngayTaoLich_str, '%Y-%m-%d').date()  # Chuyển đổi chuỗi thành đối tượng date

        for ds in dslk:
            if ds.NgayTao == ngayTaoLich:
                flat = False
                break

        if flat:
            utils.create_one_schedule(ngayTaoLich)

            return render_template('create_schedule.html', date=date)
        else:
            err_msg = "Lịch ngày khám " + str(ngayTaoLich_str) + " này đã tồn tại, vui lòng tạo lịch với 1 ngày khác"

    return render_template('create_schedule.html', date=date, err_msg=err_msg)


@app.route('/create-medical-form')
@login_required
def create_medical_form():
    err_msg = ""
    nguoiDung_id = request.args.get('nguoiDung_id')
    trieuChung = request.args.get('trieuChung')
    chuanDoan = request.args.get('chuanDoan')
    bacSy = request.args.get('bacSy')

    list_thuoc = utils.list_thuoc()

    if trieuChung and chuanDoan and bacSy:
        utils.add_phieu_kham(trieuChung, chuanDoan, bacSy, nguoiDung_id)
        err_msg = "Lập phiếu khám thành công"
        return render_template('create_medical_form.html', date=date, list_thuoc=list_thuoc, err_msg=err_msg)
    else:
        err_msg = "Không được để trống thông tin"

    return render_template('create_medical_form.html', date=date, list_thuoc=list_thuoc)


@app.route('/hoa-don')
def hoa_don():
    # db.session.query(HoaDonThuoc).delete()
    # danh_sach_tong_tien = utils.tinh_tien_thuoc()
    #
    # for phieuKham_id, ngayKham, HoTen, tienThuoc in danh_sach_tong_tien:
    #     utils.add_hoa_don(tienThuoc=tienThuoc,
    #                       trangThai=True, phieuKham_id=phieuKham_id)
    hoTen = request.args.get('hoTen')
    load_ds_hoa_don = utils.load_ds_hoa_don(hoTen=hoTen)

    return render_template('hoa_don.html', load_ds_hoa_don=load_ds_hoa_don)


@app.route('/api/add-thuoc', methods=['post'])
def add_to_toa_thuoc():
    data = request.json
    id = str(data.get('id'))
    tenThuoc = data.get('tenThuoc')
    giaBan = data.get('giaBan')

    toaThuoc = session.get('toaThuoc')

    if not toaThuoc:
        toaThuoc = {}

    if id in toaThuoc:
        toaThuoc[id]['soLuong'] = toaThuoc[id]['soLuong'] + 1
    else:
        toaThuoc[id] = {
            'id': id,
            'tenThuoc': tenThuoc,
            'giaBan': giaBan,
            'soLuong': 1
        }
    session['toaThuoc'] = toaThuoc

    return jsonify(utils.count_thuoc_of_toa_thuoc(toaThuoc))


@app.route('/toa-thuoc')
def toa_thuoc():
    err_msg = ""
    ds_phieu_kham = utils.load_phieu_kham()
    stats = utils.count_thuoc_of_toa_thuoc(session.get('toaThuoc'))
    # Lấy giá trị phieuKham_id từ tham số truy vấn
    phieuKham_id = request.args.get('phieuKham_id')
    tongTienThuoc = request.args.get('tongTienThuoc')

    if phieuKham_id:  # Kiểm tra xem phieuKham_id có tồn tại không
        utils.add_chitiethoadon(session.get('toaThuoc'), phieuKham_id)
        utils.add_hoa_don(float(tongTienThuoc), phieuKham_id)
        del session['toaThuoc']
        err_msg = "Thêm toa thuốc thành công"
        return render_template('toa_thuoc.html', ds_phieu_kham=ds_phieu_kham,
                               stats=stats, err_msg=err_msg)
    else:
        # Xử lý khi không có phieuKham_id
        pass

    return render_template('toa_thuoc.html', ds_phieu_kham=ds_phieu_kham,
                           stats=stats, err_msg=err_msg)


if __name__ == "__main__":
    app.run(debug=True)
