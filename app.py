from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'rahasia_gudang'
app.config['UPLOAD_FOLDER'] = 'static/img'

def init_db():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_inventraa'
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_admin (
                    id_admin INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    status VARCHAR(50),
                    foto_profil VARCHAR(255) DEFAULT '/static/img/logoinventra.png'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_user (
                    id_user INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    status VARCHAR(50),
                    dibuat_oleh INT,
                    foto_profil VARCHAR(255) DEFAULT '/static/img/logoinventra.png',
                    FOREIGN KEY (dibuat_oleh) REFERENCES tb_admin(id_admin) ON UPDATE CASCADE ON DELETE SET NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_supplier (
                    id_supplier INT AUTO_INCREMENT PRIMARY KEY,
                    nama_supplier VARCHAR(100) NOT NULL,
                    alamat TEXT NOT NULL,
                    no_telp VARCHAR(15) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_brgmasuk (
                    id_barang INT AUTO_INCREMENT PRIMARY KEY,
                    kode_barang VARCHAR(50) NOT NULL,
                    nama_barang VARCHAR(100) NOT NULL,
                    tgl_masuk DATE NOT NULL,
                    jumlah_barang INT NOT NULL,
                    id_supplier INT NOT NULL,
                    UNIQUE (kode_barang),
                    FOREIGN KEY (id_supplier) REFERENCES tb_supplier(id_supplier) ON DELETE RESTRICT ON UPDATE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_brgkeluar (
                    id_brgkeluar INT AUTO_INCREMENT PRIMARY KEY,
                    id_barang INT NOT NULL,
                    kode_barang VARCHAR(50) NOT NULL,
                    nama_barang VARCHAR(100) NOT NULL,
                    tgl_keluar DATE NOT NULL,
                    jumlah_barang INT NOT NULL,
                    tujuan VARCHAR(100) NOT NULL,
                    status ENUM('dalam perjalanan', 'segera tiba', 'terdistribusi') NOT NULL DEFAULT 'dalam perjalanan',
                    id_reseller INT,
                    FOREIGN KEY (id_barang) REFERENCES tb_brgmasuk(id_barang) ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (kode_barang) REFERENCES tb_brgmasuk(kode_barang) ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (id_reseller) REFERENCES tb_reseller(id_reseller) ON DELETE SET NULL ON UPDATE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_reseller (
                    id_reseller INT AUTO_INCREMENT PRIMARY KEY,
                    nama_toko VARCHAR(100) NOT NULL,
                    nama_pemilik VARCHAR(100) NOT NULL,
                    alamat TEXT NOT NULL,
                    no_telp VARCHAR(15) NOT NULL,
                    UNIQUE (no_telp)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_manajer (
                    id_manajer INT AUTO_INCREMENT PRIMARY KEY,
                    nama_manajer VARCHAR(100) NOT NULL
                )
            """)
            conn.commit()
            print("Database and tables initialized successfully!")
    except pymysql.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_photo(file):
    if file and allowed_file(file.filename):
        filename = f"profile_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return f"/static/img/{filename}"
    return None

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='db_inventraa',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.template_filter('format_date')
def format_date(value):
    if value:
        return value.strftime('%d-%m-%Y')
    return value

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            error = "Username dan password wajib diisi!"
            return render_template('login.html', error=error)
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_admin, username, status, foto_profil FROM tb_admin WHERE username=%s AND password=%s", (username, password))
            admin = cursor.fetchone()
            if admin and (admin['status'] == 'admin' or admin['status'] is None):
                session['user'] = {'id': admin['id_admin'], 'username': username, 'status': 'admin', 'foto_profil': admin['foto_profil']}
                return redirect(url_for('index'))
            
            cursor.execute("SELECT id_user, username, status, foto_profil FROM tb_user WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user and user['status'] == 'user':
                session['user'] = {'id': user['id_user'], 'username': username, 'status': 'user', 'foto_profil': user['foto_profil']}
                return redirect(url_for('index'))
            
            error = "Login gagal! Username atau password salah."
        except pymysql.Error as e:
            print(f"Error during login: {e}")
            error = "Terjadi error saat login. Coba lagi."
        finally:
            if conn:
                conn.close()
    return render_template('login.html', error=error)

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    if not isinstance(session['user'], dict):
        return "Sesi tidak valid, silakan login ulang", 500
    username = session['user'].get('username')
    status = session['user'].get('status')
    if not username or not status:
        return "Data sesi tidak lengkap, silakan login ulang", 500
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bm.id_barang, bm.kode_barang, bm.nama_barang, bm.tgl_masuk, bm.jumlah_barang,
                   s.nama_supplier, s.alamat, s.no_telp
            FROM tb_brgmasuk bm
            LEFT JOIN tb_supplier s ON bm.id_supplier = s.id_supplier
        """)
        barang = cursor.fetchall()
        welcome_message = f"Haloo selamat datang {username} sebagai {status}"
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        return render_template('index.html', barang=barang, welcome_message=welcome_message, foto_profil=foto_profil)
    except pymysql.Error as e:
        print(f"Database error in index: {e}")
        return "Terjadi error saat mengambil data. Periksa log untuk detail.", 500
    finally:
        if conn:
            conn.close()

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            kode = request.form.get('kode')
            nama = request.form.get('nama')
            tgl_masuk = request.form.get('tanggal_masuk')
            jumlah_barang = request.form.get('stok')
            nama_supplier = request.form.get('nama_supplier')
            alamat_supplier = request.form.get('alamat_supplier')
            no_telp_supplier = request.form.get('no_telp_supplier')

            if not all([kode, nama, tgl_masuk, jumlah_barang, nama_supplier, alamat_supplier, no_telp_supplier]):
                return "Semua field wajib diisi!", 400
            
            jumlah_barang = int(jumlah_barang)
            if jumlah_barang <= 0:
                return "Jumlah barang harus lebih dari 0!", 400

            cursor.execute(
                "INSERT INTO tb_supplier (nama_supplier, alamat, no_telp) VALUES (%s, %s, %s)",
                (nama_supplier, alamat_supplier, no_telp_supplier)
            )
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID() AS id_supplier")
            id_supplier = cursor.fetchone()['id_supplier']

            cursor.execute(
                "INSERT INTO tb_brgmasuk (kode_barang, nama_barang, tgl_masuk, jumlah_barang, id_supplier) VALUES (%s, %s, %s, %s, %s)",
                (kode, nama, tgl_masuk, jumlah_barang, id_supplier)
            )
            conn.commit()
            return redirect(url_for('index'))
        
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('add_item.html', foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in add_item: {e}")
        return "Terjadi error saat menambah barang.", 500
    finally:
        if conn:
            conn.close()

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session or session['user']['status'] != 'admin':
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            status = request.form.get('status')  # Tambahin status, tapi ini optional di HTML awal, jadi default ke 'user'
            admin_id = session['user']['id']

            if not all([username, password]):
                return jsonify({"message": "Semua field wajib diisi!"}), 400
            
            # Validasi panjang karakter
            if len(username) > 100 or len(password) > 100:
                return jsonify({"message": "Username dan password tidak boleh lebih dari 100 karakter!"}), 400
            
            # Cek apakah username sudah ada
            cursor.execute("SELECT id_user FROM tb_user WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({"message": "Username sudah digunakan!"}), 400

            # Default status ke 'user' jika tidak ada
            if not status:
                status = 'user'

            cursor.execute(
                "INSERT INTO tb_user (username, password, status, dibuat_oleh, foto_profil) VALUES (%s, %s, %s, %s, '/static/img/logoinventra.png')",
                (username, password, status, admin_id)
            )
            conn.commit()
            return jsonify({"message": "User berhasil ditambahkan!"})

        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('add_user.html', foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in add_user: {e}")
        return jsonify({"message": f"Terjadi error saat menambah user: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            kode = request.form.get('kode')
            nama = request.form.get('nama')
            tgl_masuk = request.form.get('tanggal_masuk')
            jumlah_barang = request.form.get('stok')
            nama_supplier = request.form.get('nama_supplier')
            alamat_supplier = request.form.get('alamat_supplier')
            no_telp_supplier = request.form.get('no_telp_supplier')

            if not all([kode, nama, tgl_masuk, jumlah_barang, nama_supplier, alamat_supplier, no_telp_supplier]):
                return "Semua field wajib diisi!", 400
            
            jumlah_barang = int(jumlah_barang)
            if jumlah_barang <= 0:
                return "Jumlah barang harus lebih dari 0!", 400

            cursor.execute("SELECT id_supplier FROM tb_brgmasuk WHERE id_barang=%s", (id,))
            id_supplier = cursor.fetchone()['id_supplier']
            cursor.execute(
                "UPDATE tb_supplier SET nama_supplier=%s, alamat=%s, no_telp=%s WHERE id_supplier=%s",
                (nama_supplier, alamat_supplier, no_telp_supplier, id_supplier)
            )
            cursor.execute(
                "UPDATE tb_brgmasuk SET kode_barang=%s, nama_barang=%s, tgl_masuk=%s, jumlah_barang=%s WHERE id_barang=%s",
                (kode, nama, tgl_masuk, jumlah_barang, id)
            )
            conn.commit()
            return redirect(url_for('barang_masuk'))
        
        cursor.execute("""
            SELECT bm.*, s.nama_supplier, s.alamat, s.no_telp 
            FROM tb_brgmasuk bm 
            JOIN tb_supplier s ON bm.id_supplier = s.id_supplier 
            WHERE bm.id_barang=%s
        """, (id,))
        barang = cursor.fetchone()
        if not barang:
            return "Barang tidak ditemukan!", 404
        
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('edit_item.html', barang=barang, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in edit_item: {e}")
        return "Terjadi error saat mengedit barang.", 500
    finally:
        if conn:
            conn.close()

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_item(id):
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Silakan login terlebih dahulu!"}), 403
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cek apakah barang ada
        cursor.execute("SELECT id_barang FROM tb_brgmasuk WHERE id_barang = %s", (id,))
        barang = cursor.fetchone()
        if not barang:
            return jsonify({"status": "error", "message": "Barang tidak ditemukan!"}), 404
        
        # Cek apakah barang masih digunakan di tb_brgkeluar
        cursor.execute("SELECT id_brgkeluar FROM tb_brgkeluar WHERE id_barang = %s", (id,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Barang tidak bisa dihapus karena sudah didistribusikan!"}), 400
        
        # Hapus data
        cursor.execute("DELETE FROM tb_brgmasuk WHERE id_barang = %s", (id,))
        conn.commit()
        
        return jsonify({"status": "success", "message": "Barang berhasil dihapus!"})
    
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in delete_item: {e}")
        return jsonify({"status": "error", "message": f"Terjadi error saat menghapus barang: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/distribusi')
def distribusi():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bk.id_brgkeluar, bm.id_barang, bm.kode_barang, bm.nama_barang, 
                   bk.tgl_keluar, bk.jumlah_barang, bk.tujuan, bk.status, r.nama_toko
            FROM tb_brgkeluar bk
            JOIN tb_brgmasuk bm ON bm.id_barang = bk.id_barang
            LEFT JOIN tb_reseller r ON bk.id_reseller = r.id_reseller
            WHERE bk.id_brgkeluar IS NOT NULL
        """)
        barang = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('distribusi.html', barang=barang, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in distribusi: {e}")
        return "Terjadi error saat mengambil data distribusi.", 500
    finally:
        if conn:
            conn.close()

@app.route('/jadwal_pengiriman')
def jadwal_pengiriman():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bk.id_brgkeluar, bk.id_barang, bk.kode_barang, bk.nama_barang, 
                   bk.tgl_keluar, bk.jumlah_barang, bk.tujuan, bk.status, bk.id_reseller
            FROM tb_brgkeluar bk
            WHERE bk.id_brgkeluar IS NOT NULL
            ORDER BY bk.tgl_keluar DESC
        """)
        keluar = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('jadwal_pengiriman.html', keluar=keluar, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in jadwal_pengiriman: {e}")
        return "Terjadi error saat mengambil jadwal pengiriman.", 500
    finally:
        if conn:
            conn.close()

@app.route('/add_pengiriman', methods=['GET', 'POST'])
def add_pengiriman():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    error_message = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            id_barang = int(request.form.get('id_barang', 0))
            tgl_keluar = request.form.get('tanggal_keluar')
            jumlah_barang = int(request.form.get('jumlah_barang', 0))
            tujuan = request.form.get('tujuan')
            status = request.form.get('status')
            nama_toko = request.form.get('nama_toko')
            nama_pemilik = request.form.get('nama_pemilik')
            alamat = request.form.get('alamat')
            no_telp = request.form.get('no_telp')

            if not all([id_barang, tgl_keluar, jumlah_barang > 0, tujuan, status, nama_toko, nama_pemilik, alamat, no_telp]):
                error_message = "Semua field wajib diisi dengan data yang valid!"
                raise ValueError(error_message)

            if not (10 <= len(no_telp) <= 15) or not no_telp.isdigit():
                error_message = "Nomor telepon harus 10-15 digit angka!"
                raise ValueError(error_message)

            valid_statuses = ['dalam perjalanan', 'segera tiba', 'terdistribusi']
            if status not in valid_statuses:
                error_message = "Status tidak valid!"
                raise ValueError(error_message)

            if len(nama_toko) > 100 or len(nama_pemilik) > 100 or len(tujuan) > 100:
                error_message = "Nama toko, nama pemilik, atau tujuan tidak boleh lebih dari 100 karakter!"
                raise ValueError(error_message)

            conn.begin()

            cursor.execute("SELECT id_barang, kode_barang, nama_barang, jumlah_barang FROM tb_brgmasuk WHERE id_barang = %s", (id_barang,))
            barang = cursor.fetchone()
            if not barang:
                error_message = "Barang tidak ditemukan! Mungkin barang sudah dihapus."
                raise ValueError(error_message)

            stok_sekarang = barang['jumlah_barang']
            if stok_sekarang < jumlah_barang:
                error_message = f"Stok tidak cukup! Stok saat ini: {stok_sekarang}, diminta: {jumlah_barang}"
                raise ValueError(error_message)

            kode_barang = barang['kode_barang']
            nama_barang = barang['nama_barang']

            cursor.execute("SELECT kode_barang FROM tb_brgmasuk WHERE id_barang = %s AND kode_barang = %s", (id_barang, kode_barang))
            if not cursor.fetchone():
                error_message = "Data barang tidak konsisten! Mungkin barang sudah diubah atau dihapus."
                raise ValueError(error_message)

            cursor.execute("SELECT id_reseller FROM tb_reseller WHERE no_telp = %s", (no_telp,))
            existing_reseller = cursor.fetchone()
            if existing_reseller:
                id_reseller = existing_reseller['id_reseller']
            else:
                cursor.execute(
                    "INSERT INTO tb_reseller (nama_toko, nama_pemilik, alamat, no_telp) VALUES (%s, %s, %s, %s)",
                    (nama_toko, nama_pemilik, alamat, no_telp)
                )
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID() AS id_reseller")
                id_reseller = cursor.fetchone()['id_reseller']

            cursor.execute(
                "INSERT INTO tb_brgkeluar (id_barang, kode_barang, nama_barang, tgl_keluar, jumlah_barang, tujuan, status, id_reseller) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (id_barang, kode_barang, nama_barang, tgl_keluar, jumlah_barang, tujuan, status, id_reseller)
            )
            cursor.execute(
                "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang - %s WHERE id_barang = %s",
                (jumlah_barang, id_barang)
            )
            conn.commit()
            return redirect(url_for('jadwal_pengiriman'))

        cursor.execute("SELECT id_barang, kode_barang, nama_barang, jumlah_barang FROM tb_brgmasuk")
        barang_list = cursor.fetchall() or []
        if not barang_list:
            error_message = "Belum ada barang yang tersedia untuk didistribusikan. Tambah barang terlebih dahulu!"
        
        today_date = datetime.today().strftime('%Y-%m-%d')
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('add_pengiriman.html', barang_list=barang_list, foto_profil=foto_profil, welcome_message=welcome_message, error_message=error_message, today_date=today_date)
    except ValueError as ve:
        if conn:
            conn.rollback()
        print(f"Validation error in add_pengiriman: {ve}")
        error_message = str(ve)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in add_pengiriman: {e}")
        error_message = "Gagal menyimpan data ke database. Pastikan data valid dan coba lagi!"
    finally:
        if conn:
            conn.close()
    
    today_date = datetime.today().strftime('%Y-%m-%d')
    barang_list = []
    foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
    welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
    return render_template('add_pengiriman.html', barang_list=barang_list, foto_profil=foto_profil, welcome_message=welcome_message, error_message=error_message, today_date=today_date)

@app.route('/edit_pengiriman/<int:id>', methods=['GET', 'POST'])
def edit_pengiriman(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            tgl_keluar = request.form.get('tanggal_keluar')
            jumlah_barang = int(request.form.get('jumlah_barang'))
            tujuan = request.form.get('tujuan')
            status = request.form.get('status')
            id_barang = int(request.form.get('id_barang'))

            if not all([tgl_keluar, jumlah_barang > 0, tujuan, status, id_barang]):
                return "Semua field wajib diisi dengan data yang valid!", 400

            cursor.execute("SELECT jumlah_barang, id_barang FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
            pengiriman_lama = cursor.fetchone()
            if not pengiriman_lama:
                return "Pengiriman tidak ditemukan!", 404
            
            selisih = jumlah_barang - pengiriman_lama['jumlah_barang']
            if selisih > 0:
                cursor.execute("SELECT jumlah_barang FROM tb_brgmasuk WHERE id_barang = %s", (id_barang,))
                stok_sekarang = cursor.fetchone()['jumlah_barang']
                if stok_sekarang < selisih:
                    return "Stok tidak cukup untuk penambahan!", 400

            cursor.execute(
                "UPDATE tb_brgkeluar SET tgl_keluar = %s, jumlah_barang = %s, tujuan = %s, status = %s WHERE id_brgkeluar = %s",
                (tgl_keluar, jumlah_barang, tujuan, status, id)
            )
            if selisih != 0:
                cursor.execute(
                    "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang - %s WHERE id_barang = %s",
                    (selisih, id_barang)
                )
            conn.commit()
            return redirect(url_for('jadwal_pengiriman'))

        cursor.execute("""
            SELECT bk.*, bm.id_barang
            FROM tb_brgkeluar bk
            JOIN tb_brgmasuk bm ON bk.id_barang = bm.id_barang
            WHERE bk.id_brgkeluar = %s
        """, (id,))
        pengiriman = cursor.fetchone()
        if not pengiriman:
            return "Pengiriman tidak ditemukan!", 404
        
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('edit_pengiriman.html', pengiriman=pengiriman, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in edit_pengiriman: {e}")
        return "Terjadi error saat mengedit pengiriman.", 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_pengiriman/<int:id>')
def delete_pengiriman(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT jumlah_barang, id_barang FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
        pengiriman = cursor.fetchone()
        if not pengiriman:
            return "Pengiriman tidak ditemukan!", 404
        
        jumlah_kembali = pengiriman['jumlah_barang']
        id_barang = pengiriman['id_barang']

        cursor.execute("DELETE FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
        cursor.execute(
            "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang + %s WHERE id_barang = %s",
            (jumlah_kembali, id_barang)
        )
        conn.commit()
        return redirect(url_for('jadwal_pengiriman'))
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in delete_pengiriman: {e}")
        return "Terjadi error saat menghapus pengiriman.", 500
    finally:
        if conn:
            conn.close()

@app.route('/add_distribusi', methods=['GET', 'POST'])
def add_distribusi():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    error_message = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            id_barang = int(request.form.get('id_barang', 0))
            tgl_keluar = request.form.get('tanggal_keluar')
            jumlah_barang = int(request.form.get('jumlah_barang', 0))
            tujuan = request.form.get('tujuan')
            status = request.form.get('status')
            nama_toko = request.form.get('nama_toko')
            nama_pemilik = request.form.get('nama_pemilik')
            alamat = request.form.get('alamat')
            no_telp = request.form.get('no_telp')

            if not all([id_barang, tgl_keluar, jumlah_barang > 0, tujuan, status, nama_toko, nama_pemilik, alamat, no_telp]):
                error_message = "Semua field wajib diisi dengan data yang valid!"
                raise ValueError(error_message)

            if not (10 <= len(no_telp) <= 15) or not no_telp.isdigit():
                error_message = "Nomor telepon harus 10-15 digit angka!"
                raise ValueError(error_message)

            valid_statuses = ['dalam perjalanan', 'segera tiba', 'terdistribusi']
            if status not in valid_statuses:
                error_message = "Status tidak valid!"
                raise ValueError(error_message)

            if len(nama_toko) > 100 or len(nama_pemilik) > 100 or len(tujuan) > 100:
                error_message = "Nama toko, nama pemilik, atau tujuan tidak boleh lebih dari 100 karakter!"
                raise ValueError(error_message)

            conn.begin()

            cursor.execute("SELECT id_barang, kode_barang, nama_barang, jumlah_barang FROM tb_brgmasuk WHERE id_barang = %s", (id_barang,))
            barang = cursor.fetchone()
            if not barang:
                error_message = "Barang tidak ditemukan! Mungkin barang sudah dihapus."
                raise ValueError(error_message)

            stok_sekarang = barang['jumlah_barang']
            if stok_sekarang < jumlah_barang:
                error_message = f"Stok tidak cukup! Stok saat ini: {stok_sekarang}, diminta: {jumlah_barang}"
                raise ValueError(error_message)

            kode_barang = barang['kode_barang']
            nama_barang = barang['nama_barang']

            cursor.execute("SELECT kode_barang FROM tb_brgmasuk WHERE id_barang = %s AND kode_barang = %s", (id_barang, kode_barang))
            if not cursor.fetchone():
                error_message = "Data barang tidak konsisten! Mungkin barang sudah diubah atau dihapus."
                raise ValueError(error_message)

            cursor.execute("SELECT id_reseller FROM tb_reseller WHERE no_telp = %s", (no_telp,))
            existing_reseller = cursor.fetchone()
            if existing_reseller:
                id_reseller = existing_reseller['id_reseller']
            else:
                cursor.execute(
                    "INSERT INTO tb_reseller (nama_toko, nama_pemilik, alamat, no_telp) VALUES (%s, %s, %s, %s)",
                    (nama_toko, nama_pemilik, alamat, no_telp)
                )
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID() AS id_reseller")
                id_reseller = cursor.fetchone()['id_reseller']

            cursor.execute(
                "INSERT INTO tb_brgkeluar (id_barang, kode_barang, nama_barang, tgl_keluar, jumlah_barang, tujuan, status, id_reseller) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (id_barang, kode_barang, nama_barang, tgl_keluar, jumlah_barang, tujuan, status, id_reseller)
            )
            cursor.execute(
                "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang - %s WHERE id_barang = %s",
                (jumlah_barang, id_barang)
            )
            conn.commit()
            return redirect(url_for('distribusi'))

        cursor.execute("SELECT id_barang, kode_barang, nama_barang, jumlah_barang FROM tb_brgmasuk")
        barang_list = cursor.fetchall() or []
        if not barang_list:
            error_message = "Belum ada barang yang tersedia untuk didistribusikan. Tambah barang terlebih dahulu!"
        
        today_date = datetime.today().strftime('%Y-%m-%d')
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('add_distribusi.html', barang_list=barang_list, foto_profil=foto_profil, welcome_message=welcome_message, error_message=error_message, today_date=today_date)
    except ValueError as ve:
        if conn:
            conn.rollback()
        print(f"Validation error in add_distribusi: {ve}")
        error_message = str(ve)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in add_distribusi: {e}")
        error_message = "Gagal menyimpan data ke database. Pastikan data valid dan coba lagi!"
    finally:
        if conn:
            conn.close()
    
    today_date = datetime.today().strftime('%Y-%m-%d')
    barang_list = []
    foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
    welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
    return render_template('add_distribusi.html', barang_list=barang_list, foto_profil=foto_profil, welcome_message=welcome_message, error_message=error_message, today_date=today_date)

@app.route('/edit_distribusi/<int:id>', methods=['GET', 'POST'])
def edit_distribusi(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            tgl_keluar = request.form.get('tanggal_keluar')
            jumlah_barang = int(request.form.get('jumlah_barang'))
            tujuan = request.form.get('tujuan')
            status = request.form.get('status')
            id_barang = int(request.form.get('id_barang'))

            if not all([tgl_keluar, jumlah_barang > 0, tujuan, status, id_barang]):
                return "Semua field wajib diisi dengan data yang valid!", 400

            cursor.execute("SELECT jumlah_barang, id_barang FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
            distribusi_lama = cursor.fetchone()
            if not distribusi_lama:
                return "Distribusi tidak ditemukan!", 404
            
            selisih = jumlah_barang - distribusi_lama['jumlah_barang']
            if selisih > 0:
                cursor.execute("SELECT jumlah_barang FROM tb_brgmasuk WHERE id_barang = %s", (id_barang,))
                stok_sekarang = cursor.fetchone()['jumlah_barang']
                if stok_sekarang < selisih:
                    return "Stok tidak cukup untuk penambahan!", 400

            cursor.execute(
                "UPDATE tb_brgkeluar SET tgl_keluar = %s, jumlah_barang = %s, tujuan = %s, status = %s WHERE id_brgkeluar = %s",
                (tgl_keluar, jumlah_barang, tujuan, status, id)
            )
            if selisih != 0:
                cursor.execute(
                    "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang - %s WHERE id_barang = %s",
                    (selisih, id_barang)
                )
            conn.commit()
            return redirect(url_for('distribusi'))

        cursor.execute("""
            SELECT bk.*, bm.id_barang
            FROM tb_brgkeluar bk
            JOIN tb_brgmasuk bm ON bk.id_barang = bm.id_barang
            WHERE bk.id_brgkeluar = %s
        """, (id,))
        distribusi = cursor.fetchone()
        if not distribusi:
            return "Distribusi tidak ditemukan!", 404
        
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('edit_distribusi.html', distribusi=distribusi, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in edit_distribusi: {e}")
        return "Terjadi error saat mengedit distribusi.", 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_distribusi/<int:id>')
def delete_distribusi(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT jumlah_barang, id_barang FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
        distribusi = cursor.fetchone()
        if not distribusi:
            return "Distribusi tidak ditemukan!", 404
        
        jumlah_kembali = distribusi['jumlah_barang']
        id_barang = distribusi['id_barang']

        cursor.execute("DELETE FROM tb_brgkeluar WHERE id_brgkeluar = %s", (id,))
        cursor.execute(
            "UPDATE tb_brgmasuk SET jumlah_barang = jumlah_barang + %s WHERE id_barang = %s",
            (jumlah_kembali, id_barang)
        )
        conn.commit()
        return redirect(url_for('distribusi'))
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error in delete_distribusi: {e}")
        return "Terjadi error saat menghapus distribusi.", 500
    finally:
        if conn:
            conn.close()

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    if not isinstance(session['user'], dict):
        return "Sesi tidak valid, silakan login ulang", 500
    username = session['user'].get('username')
    status = session['user'].get('status')
    user_id = session['user'].get('id')
    foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
    if not username or not status:
        return "Data sesi tidak lengkap, silakan login ulang", 500

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'upload':
                if 'foto_profil' not in request.files:
                    return jsonify({"status": "error", "message": "Tidak ada input file di form."}), 400
                file = request.files['foto_profil']
                if not file or file.filename == '':
                    return jsonify({"status": "error", "message": "Tidak ada file yang dipilih."}), 400
                if not allowed_file(file.filename):
                    return jsonify({"status": "error", "message": "Tipe file tidak diizinkan. Gunakan PNG, JPG, JPEG, atau GIF."}), 400
                
                # Hapus foto lama kalau bukan default
                old_foto = session['user'].get('foto_profil', '/static/img/logoinventra.png')
                if old_foto != '/static/img/logoinventra.png':
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_foto.replace('/static/img/', ''))
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                new_foto_path = save_profile_photo(file)
                if not new_foto_path:
                    return jsonify({"status": "error", "message": "Gagal menyimpan foto, pastikan file valid."}), 400
                
                if status == 'admin':
                    cursor.execute("UPDATE tb_admin SET foto_profil = %s WHERE id_admin = %s", (new_foto_path, user_id))
                else:
                    cursor.execute("UPDATE tb_user SET foto_profil = %s WHERE id_user = %s", (new_foto_path, user_id))
                conn.commit()
                session['user']['foto_profil'] = new_foto_path
                return jsonify({"status": "success", "message": "Foto profil berhasil diunggah."})
            
            elif action == 'delete':
                current_foto = session['user'].get('foto_profil', '/static/img/logoinventra.png')
                default_foto = '/static/img/logoinventra.png'
                if current_foto != default_foto:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], current_foto.replace('/static/img/', ''))
                    if os.path.exists(file_path):
                        os.remove(file_path)  # Hapus file fisik
                if status == 'admin':
                    cursor.execute("UPDATE tb_admin SET foto_profil = %s WHERE id_admin = %s", (default_foto, user_id))
                else:
                    cursor.execute("UPDATE tb_user SET foto_profil = %s WHERE id_user = %s", (default_foto, user_id))
                conn.commit()
                session['user']['foto_profil'] = default_foto
                return jsonify({"status": "success", "message": "Foto profil berhasil dihapus."})
            
            return jsonify({"status": "error", "message": "Aksi tidak dikenali"}), 400

        user_data = {}
        if status == 'admin':
            cursor.execute("SELECT id_admin, username, status, foto_profil FROM tb_admin WHERE id_admin=%s", (user_id,))
            user_data = cursor.fetchone()
        else:
            cursor.execute("SELECT id_user, username, status, dibuat_oleh, foto_profil FROM tb_user WHERE id_user=%s", (user_id,))
            user_data = cursor.fetchone()
            if user_data and user_data['dibuat_oleh']:
                cursor.execute("SELECT username FROM tb_admin WHERE id_admin=%s", (user_data['dibuat_oleh'],))
                admin_data = cursor.fetchone()
                user_data['created_by'] = admin_data['username'] if admin_data else 'Unknown'
        
        welcome_message = f"Haloo selamat datang {username} sebagai {status}"
        foto_profil = user_data.get('foto_profil', '/static/img/logoinventra.png')
        session['user']['foto_profil'] = foto_profil
        return render_template('profile.html', user_data=user_data, welcome_message=welcome_message, foto_profil=foto_profil)
    except pymysql.Error as e:
        print(f"Database error in profile: {e}")
        return jsonify({"status": "error", "message": "Terjadi error saat mengambil data profil."}), 500
    finally:
        if conn:
            conn.close()

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/data_admin')
def data_admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_admin, username, password, status, foto_profil FROM tb_admin")
        admins = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('data_admin.html', admins=admins, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in data_admin: {e}")
        return "Terjadi error saat mengambil data admin.", 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_admin/<int:id>', methods=['GET', 'POST'])
def delete_admin(id):
    if 'user' not in session or session['user']['status'] != 'admin':
        return jsonify({"status": "error", "message": "Hanya admin yang bisa menghapus admin!"}), 403
    
    if session['user']['id'] == id:
        return jsonify({"status": "error", "message": "Tidak dapat menghapus admin yang sedang login!"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_admin FROM tb_admin WHERE id_admin = %s", (id,))
        admin = cursor.fetchone()
        if not admin:
            return jsonify({"status": "error", "message": "Admin tidak ditemukan!"}), 404
        
        cursor.execute("DELETE FROM tb_admin WHERE id_admin = %s", (id,))
        conn.commit()
        print(f"Admin with ID {id} deleted successfully.")
        return jsonify({"status": "success", "message": "Admin berhasil dihapus!"})
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error deleting admin ID {id}: {e}")
        return jsonify({"status": "error", "message": f"Gagal menghapus admin: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/edit_admin/<int:id>', methods=['POST'])
def edit_admin(id):
    if 'user' not in session or session['user']['status'] != 'admin':
        return jsonify({"status": "error", "message": "Hanya admin yang bisa mengedit admin!"}), 403

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ambil data dari request JSON
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validasi input
        if not username or not password:
            return jsonify({"status": "error", "message": "Username dan password wajib diisi!"}), 400
        
        if len(username) > 100 or len(password) > 100:
            return jsonify({"status": "error", "message": "Username dan password tidak boleh lebih dari 100 karakter!"}), 400

        # Cek apakah admin dengan ID tersebut ada
        cursor.execute("SELECT id_admin FROM tb_admin WHERE id_admin = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Admin tidak ditemukan!"}), 404

        # Update data admin
        cursor.execute(
            "UPDATE tb_admin SET username = %s, password = %s WHERE id_admin = %s",
            (username, password, id)
        )
        affected_rows = cursor.rowcount
        conn.commit()

        if affected_rows == 0:
            return jsonify({"status": "error", "message": "Tidak ada perubahan yang dilakukan."}), 400

        print(f"Admin with ID {id} edited successfully. Username: {username}, Password: {password}")
        return jsonify({"status": "success", "message": "Admin berhasil diupdate!"})
    except pymysql.IntegrityError as e:
        if conn:
            conn.rollback()
        print(f"Integrity error updating admin ID {id}: {e}")
        return jsonify({"status": "error", "message": "Username sudah digunakan oleh admin lain!"}), 400
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error updating admin ID {id}: {e}")
        return jsonify({"status": "error", "message": f"Gagal menyimpan perubahan: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/data_user')
def data_user():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_user, u.username, u.password, u.status, u.dibuat_oleh, a.username AS created_by
            FROM tb_user u
            LEFT JOIN tb_admin a ON u.dibuat_oleh = a.id_admin
        """)
        users = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('data_user.html', users=users, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in data_user: {e}")
        return "Terjadi error saat mengambil data user.", 500
    finally:
        if conn:
            conn.close()

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    if 'user' not in session or session['user']['status'] != 'admin':
        return jsonify({"status": "error", "message": "Hanya admin yang bisa mengedit user!"}), 403
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        status = data.get('status')
        dibuat_oleh = data.get('dibuat_oleh')  # Ambil dari input, bisa username atau ID

        if not all([username, password, status]):
            return jsonify({"status": "error", "message": "Username, password, dan status wajib diisi!"}), 400
        if len(username) > 100 or len(password) > 100:
            return jsonify({"status": "error", "message": "Username dan password tidak boleh lebih dari 100 karakter!"}), 400

        # Konversi dibuat_oleh dari username ke id_admin kalau perlu
        dibuat_oleh_id = None
        if dibuat_oleh and dibuat_oleh != 'Unknown':
            cursor.execute("SELECT id_admin FROM tb_admin WHERE username = %s", (dibuat_oleh,))
            result = cursor.fetchone()
            if result:
                dibuat_oleh_id = result['id_admin']
            else:
                return jsonify({"status": "error", "message": "Admin pembuat tidak ditemukan!"}), 400
        # Jika 'Unknown' atau kosong, set NULL (sesuai foreign key constraint)
        elif not dibuat_oleh or dibuat_oleh == 'Unknown':
            dibuat_oleh_id = None

        cursor.execute(
            "UPDATE tb_user SET username = %s, password = %s, status = %s, dibuat_oleh = %s WHERE id_user = %s",
            (username, password, status, dibuat_oleh_id, id)
        )
        conn.commit()
        print(f"User with ID {id} edited successfully.")
        return jsonify({"status": "success", "message": "User berhasil diupdate!"})
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error updating user ID {id}: {e}")
        return jsonify({"status": "error", "message": f"Gagal menyimpan perubahan: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    if 'user' not in session or session['user']['status'] != 'admin':
        return jsonify({"status": "error", "message": "Hanya admin yang bisa menghapus user!"}), 403
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tb_user WHERE id_user = %s", (id,))
        conn.commit()
        print(f"User with ID {id} deleted successfully.")
        return jsonify({"status": "success", "message": "User berhasil dihapus!"})
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"Error deleting user ID {id}: {e}")
        return jsonify({"status": "error", "message": f"Gagal menghapus user: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/barang_masuk')
def barang_masuk():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bm.id_barang, bm.kode_barang, bm.nama_barang, bm.tgl_masuk, bm.jumlah_barang,
                   s.nama_supplier, s.alamat, s.no_telp
            FROM tb_brgmasuk bm
            LEFT JOIN tb_supplier s ON bm.id_supplier = s.id_supplier
        """)
        barang = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('barang_masuk.html', barang=barang, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in barang_masuk: {e}")
        return "Terjadi error saat mengambil data barang masuk.", 500
    finally:
        if conn:
            conn.close()

@app.route('/barang_keluar')
def barang_keluar():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bk.id_brgkeluar, bm.id_barang, bm.kode_barang, bm.nama_barang,
                   bk.tgl_keluar, bk.jumlah_barang, bk.tujuan, bk.status, r.nama_toko
            FROM tb_brgkeluar bk
            JOIN tb_brgmasuk bm ON bm.id_barang = bk.id_barang
            LEFT JOIN tb_reseller r ON bk.id_reseller = r.id_reseller
            WHERE bk.status = 'terdistribusi'
        """)
        barang = cursor.fetchall() or []
        foto_profil = session['user'].get('foto_profil', '/static/img/logoinventra.png')
        welcome_message = f"Haloo selamat datang {session['user']['username']} sebagai {session['user']['status']}"
        return render_template('barang_keluar.html', barang=barang, foto_profil=foto_profil, welcome_message=welcome_message)
    except pymysql.Error as e:
        print(f"Database error in barang_keluar: {e}")
        return "Terjadi error saat mengambil data barang keluar.", 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)