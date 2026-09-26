import calendar
from datetime import datetime, date, timedelta
import copy
import os
import json
from flask import (
    Flask, render_template_string, request, redirect,
    url_for, session, flash, send_from_directory
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me_in_production"

# --- YAPILANDIRMA VE SABİTLER ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- KULLANICI YÖNETİMİ HIZLI YARDIMCI FONKSİYONLAR ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def get_user_data_file(username):
    return os.path.join(USER_DATA_DIR, f"{username}.json")


# --- VARSAYILAN ŞABLON VE VERİLER ---
DEFAULT_COURSES = {
    "TÜRKÇE": [
        "Sözcükte Anlam", "Cümlede Anlam", "Paragrafta Anlam", "Ses Bilgisi",
        "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Yapı",
        "İsim / Sıfat / Zamir", "Zarf / Edat / Bağlaç / Ünlem", "Fiiller / Ek Fiil / Fiilde Çatı",
        "Fiilimsi", "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozukluğu"
    ],
    "MATEMATİK": [
        "Temel Kavramlar", "Sayı Basamakları", "Bölme - Bölünebilme", "EBOB - EKOK",
        "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü İfadeler",
        "Köklü İfadeler", "Çarpanlara Ayırma", "Oran - Orantı", "Denklem Çözme",
        "Problemler", "Mantık", "Kümeler", "Fonksiyonlar", "Polinomlar",
        "2. Dereceden Denklemler", "Karmaşık Sayılar", "Parabol", "Eşitsizlikler",
        "Permütasyon - Kombinasyon", "Olasılık", "İstatistik", "Logaritma",
        "Diziler", "Limit ve Süreklilik", "Türev", "İntegral"
    ],
    "GEOMETRİ": [
        "Açılar ve Üçgenler", "Dik Üçgen / Özel Üçgenler", "İkizkenar ve Eşkenar Üçgen",
        "Üçgende Alan", "Üçgende Açıortay / Kenarortay", "Üçgende Benzerlik",
        "Çokgenler", "Dörtgenler ve Paralelkenar", "Eşkenar Dörtgen / Deltoid",
        "Dikdörtgen / Kare", "Yamuk", "Çember ve Daire", "Analitik Geometri",
        "Katı Cisimler (Prizma, Piramit, Konu, Küre)", "Çemberin Analitiği"
    ],
    "FİZİK": [
        "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Sıvıların Kaldırma Kuvveti",
        "Basınç", "Isı, Sıcaklık ve Genleşme", "Hareket ve Kuvvet", "Dinamik",
        "İş, Güç ve Enerji", "Elektrostatik", "Elektrik Akımı ve Devreler",
        "Mıknatıs ve Manyetizma", "Dalgalar", "Optik", "Vektörler / Tork ve Denge",
        "Kütle Merkezi / Basit Makineler", "Atışlar", "İtme ve Momentum",
        "Düzgün Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği",
        "Atom Fiziği ve Radyoaktivite", "Modern Fizik"
    ],
    "KİMYA": [
        "Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler",
        "Maddenin Halleri", "Doğa ve Kimya", "Mol Kavramı", "Kimyasal Tepkimeler ve Hesaplamalar",
        "Karışımlar", "Asitler, Bazlar ve Tuzlar", "Kimya Her Yerde", "Gazlar",
        "Sıvı Çözeltiler ve Çözünürlük", "Kimyasal Tepkimelerde Enerji",
        "Kimyasal Tepkimelerde Hız", "Kimyasal Denge", "Asit-Baz Dengesi",
        "KÇÇ (Çözünürlük Dengesi)", "Kimya ve Elektrik", "Karbon Kimyasına Giriş",
        "Organik Kimya"
    ],
    "BİYOLOJİ": [
        "Yaşam Bilimi Biyoloji", "Hücre ve Organeller", "Canlıların Sınıflandırılması",
        "Hücre Bölünmeleri (Mitoz / Mayoz)", "Kalıtım", "Ekosistem Ekolojisi",
        "İnsan Fizyolojisi (Sistemler)", "Göz ve Duyu Organları", "Nükleik Asitler ve Protein Sentezi",
        "Hücresel Solunum ve Fotosentez / Kemosentez", "Bitki Biyolojisi", "Canlılar ve Çevre"
    ],
    "TARİH": [
        "Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya",
        "İlk ve Orta Çağlarda Türk Dünyası", "İslam Medeniyetinin Doğuşu",
        "İlk Türk İslam Devletleri", "Yerleşme ve Devletleşme Sürecinde Selçuklu Türkiye'si",
        "Beylikten Devlete Osmanlı Siyaseti", "Devletleşme Sürecinde Savaşçılar ve Askerler",
        "Beylikten Devlete Osmanlı Medeniyeti", "Dünya Gücü Osmanlı (1453-1595)",
        "Değişim Çağında Avrupa ve Osmanlı", "Uluslararası İlişkilerde Denge Stratejisi (1774-1914)",
        "Devrimler Çağında Değişen Devlet-Toplum İlişkileri", "Sermaye ve Emek",
        "XIX. ve XX. Yüzyılda Değişen Gündelik Hayat", "20. Yüzyıl Başlarında Osmanlı Devleti ve Dünya",
        "Milli Mücadele", "Atatürkçülük ve Türk İnkılabı", "İki Dünya Savaşı Arasındaki Dönem",
        "II. Dünya Savaşı", "Soğuk Savaş Dönemi", "Yumuşama Dönemi", "Küreselleşen Dünya"
    ],
    "COĞRAFYA": [
        "Doğa ve İnsan", "Dünya'nın Şekli ve Hareketleri", "Coğrafi Konum", "Harita Bilgisi",
        "Atmosfer ve İklim", "Sıcaklık / Basınç / Rüzgarlar / Nem ve Yağış", "İklim Tipleri",
        "İç ve Dış Kuvvetler", "Türkiye'nin Yer Şekilleri", "Nüfus ve Yerleşme",
        "Ekonomik Faaliyetler", "Bölgeler ve Ülkeler", "Doğal Afetler", "Ekosistem ve Biyoçeşitlilik",
        "Şehirlerin Fonksiyonları", "Türkiye'de Tarım, Hayvancılık ve Sanayi", "Küresel Ticaret ve Turizm"
    ],
    "FELSEFE": [
        "Felsefeyi Tanıma", "Felsefe ile Düşünme", "Varlık Felsefesi (Ontoloji)",
        "Bilgi Felsefesi (Epistemoloji)", "Bilim Felsefesi", "Ahlak Felsefesi (Etik)",
        "Siyaset Felsefesi", "Sanat Felsefesi (Estetik)", "Din Felsefesi", "Felsefi Okuma ve Yazma"
    ],
    "DİN KÜLTÜRÜ": [
        "Bilgi ve İnanç", "Din ve İslam", "İslam ve İbadet", "Gençlik ve Değerler",
        "Gönül Coğrafyamız", "Allah İnsan İlişkisi", "Dünya ve Ahiret", "Kur'an'a Göre Hz. Muhammed",
        "İslam Düşüncesinde Yorumlar (Mezhepler)"
    ]
}


def get_default_user_data():
    tracking = {}
    for c, topics in DEFAULT_COURSES.items():
        tracking[c] = {}
        for t in topics:
            tracking[c][t] = {"konu": False, "soru": False, "tekrar": False, "note": ""}
    return {
        "tracking": tracking,
        "daily_logs": {},  # "YYYY-MM-DD": {"solved": 0, "study_time": 0, "target": 100, "target_time": 120}
        "schedules": {},   # "YYYY-MM-DD": [{"id": 1, "task": "...", "done": False, "photo": "..."}]
        "notes": []        # [{"id": 1, "title": "...", "content": "...", "date": "..."}]
    }


def load_user_data(username):
    filepath = get_user_data_file(username)
    if not os.path.exists(filepath):
        data = get_default_user_data()
        save_user_data(username, data)
        return data
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_data = get_default_user_data()
            # Yeni eklenen ders/konuları eksiksiz senkronize et
            for c, topics in default_data["tracking"].items():
                if c not in data["tracking"]:
                    data["tracking"][c] = topics
                else:
                    for t, sub in topics.items():
                        if t not in data["tracking"][c]:
                            data["tracking"][c][t] = sub
            if "daily_logs" not in data:
                data["daily_logs"] = {}
            if "schedules" not in data:
                data["schedules"] = {}
            if "notes" not in data:
                data["notes"] = []
            return data
    except Exception:
        return get_default_user_data()


def save_user_data(username, data):
    filepath = get_user_data_file(username)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- ORTAK HTML ŞABLONU ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sınav & Ders Takip Platformu</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #50e3c2;
            --bg-color: #f4f7f6;
            --card-bg: #ffffff;
            --text-color: #333333;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar-brand { font-weight: bold; font-size: 1.4rem; }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .card-header {
            background-color: var(--card-bg);
            border-bottom: 1px solid #edf2f7;
            font-weight: 600;
        }
        .btn-primary { background-color: var(--primary-color); border: none; }
        .btn-primary:hover { background-color: #357abd; }
        .progress { height: 10px; border-radius: 5px; }
        .status-badge { font-size: 0.8rem; padding: 4px 8px; border-radius: 4px; }
        .stat-card {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border-radius: 12px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}"><i class="fa-solid fa-graduation-cap me-2"></i>DersTakip</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                {% if session.get('user') %}
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}"><i class="fa-solid fa-chart-line me-1"></i> Panel</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('tracking') }}"><i class="fa-solid fa-book-open me-1"></i> Konu Takibi</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('daily_log') }}"><i class="fa-solid fa-check-double me-1"></i> Günlük Soru / Süre</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('schedule') }}"><i class="fa-solid fa-calendar-days me-1"></i> Takvim & Program</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('notes') }}"><i class="fa-solid fa-note-sticky me-1"></i> Notlarım</a></li>
                </ul>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><span class="nav-link text-light"><i class="fa-solid fa-user me-1"></i> {{ session['user'] }}</span></li>
                    <li class="nav-item"><a class="nav-link text-danger" href="{{ url_for('logout') }}"><i class="fa-solid fa-right-from-bracket me-1"></i> Çıkış</a></li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# --- ROTALAR / YÖNLENDİRMELER ---

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        users = load_users()
        if username in users and users[username] == password:
            session["user"] = username
            flash("Başarıyla giriş yapıldı!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Hatalı kullanıcı adı veya şifre!", "danger")

    login_html = """
    {% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5">
        <div class="col-md-4">
            <div class="card p-4">
                <h3 class="text-center mb-4">Giriş Yap</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Kullanıcı Adı</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Şifre</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Giriş</button>
                </form>
                <div class="mt-3 text-center">
                    <a href="{{ url_for('register') }}">Hesabın yok mu? Kayıt Ol</a>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", login_html))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        users = load_users()

        if username in users:
            flash("Bu kullanıcı adı zaten alınmış!", "warning")
        elif not username or not password:
            flash("Lütfen tüm alanları doldurun!", "warning")
        else:
            users[username] = password
            save_users(users)
            load_user_data(username)  # Varsayılan json yapısını oluştur
            flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for("login"))

    reg_html = """
    {% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5">
        <div class="col-md-4">
            <div class="card p-4">
                <h3 class="text-center mb-4">Kayıt Ol</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Kullanıcı Adı</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Şifre</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">Kayıt Ol</button>
                </form>
                <div class="mt-3 text-center">
                    <a href="{{ url_for('login') }}">Zaten hesabın var mı? Giriş Yap</a>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", reg_html))


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Oturum kapatıldı.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    tracking = user_data.get("tracking", {})

    # Genel Tamamlanma Oranları
    course_stats = {}
    total_topics = 0
    completed_topics = 0

    for course, topics in tracking.items():
        c_total = len(topics)
        c_done = sum(1 for t, val in topics.items() if val.get("konu") and val.get("soru"))
        percent = int((c_done / c_total) * 100) if c_total > 0 else 0
        course_stats[course] = {"total": c_total, "done": c_done, "percent": percent}

        total_topics += c_total
        completed_topics += c_done

    overall_percent = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

    # Günlük Soru İstatistikleri Grafik Verisi (Son 7 Gün)
    today = date.today()
    last_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    chart_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%d %b") for d in last_7_days]
    chart_questions = [user_data.get("daily_logs", {}).get(d, {}).get("solved", 0) for d in last_7_days]
    chart_times = [user_data.get("daily_logs", {}).get(d, {}).get("study_time", 0) for d in last_7_days]

    dash_html = f"""
    <div class="row">
        <div class="col-md-4">
            <div class="stat-card mb-4 text-center">
                <h2>%{overall_percent}</h2>
                <p class="mb-0">Genel Müfredat Tamamlanma Oranı</p>
                <small>{completed_topics} / {total_topics} Konu Bitti</small>
            </div>
        </div>
        <div class="col-md-8">
            <div class="card p-3">
                <h5>Son 7 Günlük Soru / Süre Grafiği</h5>
                <canvas id="weeklyChart" height="100"></canvas>
            </div>
        </div>
    </div>

    <h4 class="mt-4 mb-3">Ders Bazlı İlerleme</h4>
    <div class="row">
        {% for course, stat in course_stats.items() %}
        <div class="col-md-4">
            <div class="card p-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0 fw-bold">{{ course }}</h6>
                    <span class="badge bg-primary">%{ stat.percent }</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-success" style="width: {{ stat.percent }}%"></div>
                </div>
                <small class="text-muted mt-2 d-block">{{ stat.done }} / {{ stat.total }} Konu Tamamlandı</small>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        const ctx = document.getElementById('weeklyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [
                    {{
                        label: 'Çözülen Soru',
                        data: {json.dumps(chart_questions)},
                        borderColor: '#4a90e2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        fill: true,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Çalışma Süresi (Dakika)',
                        data: {json.dumps(chart_times)},
                        borderColor: '#50e3c2',
                        backgroundColor: 'rgba(80, 227, 194, 0.1)',
                        fill: true,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                scales: {{
                    y: {{ type: 'linear', position: 'left' }},
                    y1: {{ type: 'linear', position: 'right', grid: {{ drawOnChartArea: false }} }}
                }}
            }}
        }});
    </script>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", dash_html),
        course_stats=course_stats
    )


@app.route("/tracking", methods=["GET", "POST"])
def tracking():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])

    if request.method == "POST":
        # Form güncellemelerini kaydet
        for course, topics in user_data["tracking"].items():
            for topic in topics.keys():
                k_key = f"konu_{course}_{topic}"
                s_key = f"soru_{course}_{topic}"
                t_key = f"tekrar_{course}_{topic}"
                n_key = f"note_{course}_{topic}"

                user_data["tracking"][course][topic]["konu"] = k_key in request.form
                user_data["tracking"][course][topic]["soru"] = s_key in request.form
                user_data["tracking"][course][topic]["tekrar"] = t_key in request.form
                user_data["tracking"][course][topic]["note"] = request.form.get(n_key, "")

        save_user_data(session["user"], user_data)
        flash("İlerlemeleriniz başarıyla kaydedildi!", "success")
        return redirect(url_for("tracking"))

    selected_course = request.args.get("course", list(DEFAULT_COURSES.keys())[0])

    track_html = """
    <div class="card p-3 mb-4">
        <div class="d-flex flex-wrap gap-2">
            {% for c in courses %}
                <a href="{{ url_for('tracking', course=c) }}" class="btn btn-outline-primary {% if c == selected_course %}active{% endif %}">
                    {{ c }}
                </a>
            {% endfor %}
        </div>
    </div>

    <form method="POST">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">{{ selected_course }} Konu Listesi</h5>
                <button type="submit" class="btn btn-success"><i class="fa-solid fa-floppy-disk me-1"></i> Değişiklikleri Kaydet</button>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Konu Adı</th>
                                <th class="text-center">Konu Anlatımı</th>
                                <th class="text-center">Soru Çözümü</th>
                                <th class="text-center">Tekrar Yapıldı</th>
                                <th>Özel Not</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for topic, data in tracking[selected_course].items() %}
                            <tr>
                                <td><strong>{{ topic }}</strong></td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="konu_{{selected_course}}_{{topic}}" {% if data.konu %}checked{% endif %}>
                                </td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="soru_{{selected_course}}_{{topic}}" {% if data.soru %}checked{% endif %}>
                                </td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="tekrar_{{selected_course}}_{{topic}}" {% if data.tekrar %}checked{% endif %}>
                                </td>
                                <td>
                                    <input type="text" class="form-control form-control-sm" name="note_{{selected_course}}_{{topic}}" value="{{ data.note }}" placeholder="Not ekle...">
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </form>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", track_html),
        courses=list(DEFAULT_COURSES.keys()),
        selected_course=selected_course,
        tracking=user_data["tracking"]
    )


@app.route("/daily_log", methods=["GET", "POST"])
def daily_log():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    selected_date = request.args.get("date", date.today().strftime("%Y-%m-%d"))

    if request.method == "POST":
        solved = int(request.form.get("solved", 0))
        study_time = int(request.form.get("study_time", 0))
        target = int(request.form.get("target", 100))
        target_time = int(request.form.get("target_time", 120))

        if "daily_logs" not in user_data:
            user_data["daily_logs"] = {}

        user_data["daily_logs"][selected_date] = {
            "solved": solved,
            "study_time": study_time,
            "target": target,
            "target_time": target_time
        }

        save_user_data(session["user"], user_data)
        flash("Günlük veriler kaydedildi!", "success")
        return redirect(url_for("daily_log", date=selected_date))

    log_data = user_data.get("daily_logs", {}).get(selected_date, {
        "solved": 0, "study_time": 0, "target": 100, "target_time": 120
    })

    log_html = """
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4">
                <h4>Günlük Çalışma & Soru Kaydı</h4>
                <form method="GET" class="mb-4">
                    <label class="form-label">Tarih Seç</label>
                    <input type="date" name="date" class="form-control" value="{{ selected_date }}" onchange="this.form.submit()">
                </form>
                <hr>
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Çözülen Soru</label>
                            <input type="number" name="solved" class="form-control" value="{{ log_data.solved }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Hedef Soru</label>
                            <input type="number" name="target" class="form-control" value="{{ log_data.target }}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Çalışma Süresi (Dk)</label>
                            <input type="number" name="study_time" class="form-control" value="{{ log_data.study_time }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Hedef Süre (Dk)</label>
                            <input type="number" name="target_time" class="form-control" value="{{ log_data.target_time }}">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Kaydet</button>
                </form>
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", log_html),
        selected_date=selected_date,
        log_data=log_data
    )


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    selected_date = request.args.get("date", date.today().strftime("%Y-%m-%d"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            task = request.form.get("task")
            file = request.files.get("photo")
            filename = ""

            if file and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                filename = f"{session['user']}_{int(datetime.now().timestamp())}_{fname}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            if selected_date not in user_data["schedules"]:
                user_data["schedules"][selected_date] = []

            user_data["schedules"][selected_date].append({
                "id": int(datetime.now().timestamp() * 1000),
                "task": task,
                "done": False,
                "photo": filename
            })

        elif action == "toggle":
            task_id = int(request.form.get("task_id"))
            for t in user_data["schedules"].get(selected_date, []):
                if t["id"] == task_id:
                    t["done"] = not t["done"]

        elif action == "delete":
            task_id = int(request.form.get("task_id"))
            user_data["schedules"][selected_date] = [
                t for t in user_data["schedules"].get(selected_date, []) if t["id"] != task_id
            ]

        save_user_data(session["user"], user_data)
        return redirect(url_for("schedule", date=selected_date))

    tasks = user_data.get("schedules", {}).get(selected_date, [])

    sch_html = """
    <div class="row">
        <div class="col-md-5">
            <div class="card p-3">
                <h5>Tarih Seçin</h5>
                <form method="GET">
                    <input type="date" name="date" class="form-control mb-3" value="{{ selected_date }}" onchange="this.form.submit()">
                </form>
                <hr>
                <h6>Yeni Görev / Program Ekle</h6>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="add">
                    <div class="mb-3">
                        <input type="text" name="task" class="form-control" placeholder="Örn: 2 Saat Matematik Çözülecek" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Soru Fotoğrafı / Ek (Opsiyonel)</label>
                        <input type="file" name="photo" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Ekle</button>
                </form>
            </div>
        </div>

        <div class="col-md-7">
            <div class="card p-3">
                <h5>{{ selected_date }} Tarihindeki Programım</h5>
                {% if tasks %}
                    <ul class="list-group list-group-flush">
                        {% for t in tasks %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <div>
                                    <form method="POST" style="display:inline;">
                                        <input type="hidden" name="action" value="toggle">
                                        <input type="hidden" name="task_id" value="{{ t.id }}">
                                        <button type="submit" class="btn btn-sm {% if t.done %}btn-success{% else %}btn-outline-secondary{% endif %} me-2">
                                            <i class="fa-solid fa-check"></i>
                                        </button>
                                    </form>
                                    <span style="{% if t.done %}text-decoration: line-through; color: gray;{% endif %}">
                                        {{ t.task }}
                                    </span>
                                    {% if t.photo %}
                                        <br>
                                        <a href="{{ url_for('uploaded_file', filename=t.photo) }}" target="_blank" class="badge bg-info text-decoration-none mt-1">
                                            <i class="fa-solid fa-image"></i> Fotoğrafı Gör
                                        </a>
                                    {% endif %}
                                </div>
                                <form method="POST">
                                    <input type="hidden" name="action" value="delete">
                                    <input type="hidden" name="task_id" value="{{ t.id }}">
                                    <button type="submit" class="btn btn-sm btn-danger"><i class="fa-solid fa-trash"></i></button>
                                </form>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted mt-2">Bu tarihe ait program eklenmemiş.</p>
                {% endif %}
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", sch_html),
        selected_date=selected_date,
        tasks=tasks
    )


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            title = request.form.get("title")
            content = request.form.get("content")
            user_data["notes"].append({
                "id": int(datetime.now().timestamp() * 1000),
                "title": title,
                "content": content,
                "date": date.today().strftime("%Y-%m-%d")
            })

        elif action == "delete":
            note_id = int(request.form.get("note_id"))
            user_data["notes"] = [n for n in user_data["notes"] if n["id"] != note_id]

        save_user_data(session["user"], user_data)
        return redirect(url_for("notes"))

    notes_html = """
    <div class="row">
        <div class="col-md-4">
            <div class="card p-3">
                <h5>Yeni Not Ekle</h5>
                <form method="POST">
                    <input type="hidden" name="action" value="add">
                    <div class="mb-3">
                        <input type="text" name="title" class="form-control" placeholder="Başlık" required>
                    </div>
                    <div class="mb-3">
                        <textarea name="content" class="form-control" rows="5" placeholder="Not detayları..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Kaydet</button>
                </form>
            </div>
        </div>

        <div class="col-md-8">
            <div class="row">
                {% for n in notes_list %}
                <div class="col-md-6">
                    <div class="card p-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title">{{ n.title }}</h5>
                            <form method="POST">
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="note_id" value="{{ n.id }}">
                                <button type="submit" class="btn btn-sm btn-outline-danger"><i class="fa-solid fa-trash"></i></button>
                            </form>
                        </div>
                        <p class="card-text mt-2" style="white-space: pre-wrap;">{{ n.content }}</p>
                        <small class="text-muted text-end d-block">{{ n.date }}</small>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", notes_html),
        notes_list=user_data.get("notes", [])
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --- UYGULAMA BAŞLATMA VE PORT DÜZENLEMESİ (RENDER UYUMLU) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)import calendar
from datetime import datetime, date, timedelta
import copy
import os
import json
from flask import (
    Flask, render_template_string, request, redirect,
    url_for, session, flash, send_from_directory
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me_in_production"

# --- YAPILANDIRMA VE SABİTLER ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- KULLANICI YÖNETİMİ HIZLI YARDIMCI FONKSİYONLAR ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def get_user_data_file(username):
    return os.path.join(USER_DATA_DIR, f"{username}.json")


# --- VARSAYILAN ŞABLON VE VERİLER ---
DEFAULT_COURSES = {
    "TÜRKÇE": [
        "Sözcükte Anlam", "Cümlede Anlam", "Paragrafta Anlam", "Ses Bilgisi",
        "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Yapı",
        "İsim / Sıfat / Zamir", "Zarf / Edat / Bağlaç / Ünlem", "Fiiller / Ek Fiil / Fiilde Çatı",
        "Fiilimsi", "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozukluğu"
    ],
    "MATEMATİK": [
        "Temel Kavramlar", "Sayı Basamakları", "Bölme - Bölünebilme", "EBOB - EKOK",
        "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü İfadeler",
        "Köklü İfadeler", "Çarpanlara Ayırma", "Oran - Orantı", "Denklem Çözme",
        "Problemler", "Mantık", "Kümeler", "Fonksiyonlar", "Polinomlar",
        "2. Dereceden Denklemler", "Karmaşık Sayılar", "Parabol", "Eşitsizlikler",
        "Permütasyon - Kombinasyon", "Olasılık", "İstatistik", "Logaritma",
        "Diziler", "Limit ve Süreklilik", "Türev", "İntegral"
    ],
    "GEOMETRİ": [
        "Açılar ve Üçgenler", "Dik Üçgen / Özel Üçgenler", "İkizkenar ve Eşkenar Üçgen",
        "Üçgende Alan", "Üçgende Açıortay / Kenarortay", "Üçgende Benzerlik",
        "Çokgenler", "Dörtgenler ve Paralelkenar", "Eşkenar Dörtgen / Deltoid",
        "Dikdörtgen / Kare", "Yamuk", "Çember ve Daire", "Analitik Geometri",
        "Katı Cisimler (Prizma, Piramit, Konu, Küre)", "Çemberin Analitiği"
    ],
    "FİZİK": [
        "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Sıvıların Kaldırma Kuvveti",
        "Basınç", "Isı, Sıcaklık ve Genleşme", "Hareket ve Kuvvet", "Dinamik",
        "İş, Güç ve Enerji", "Elektrostatik", "Elektrik Akımı ve Devreler",
        "Mıknatıs ve Manyetizma", "Dalgalar", "Optik", "Vektörler / Tork ve Denge",
        "Kütle Merkezi / Basit Makineler", "Atışlar", "İtme ve Momentum",
        "Düzgün Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği",
        "Atom Fiziği ve Radyoaktivite", "Modern Fizik"
    ],
    "KİMYA": [
        "Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler",
        "Maddenin Halleri", "Doğa ve Kimya", "Mol Kavramı", "Kimyasal Tepkimeler ve Hesaplamalar",
        "Karışımlar", "Asitler, Bazlar ve Tuzlar", "Kimya Her Yerde", "Gazlar",
        "Sıvı Çözeltiler ve Çözünürlük", "Kimyasal Tepkimelerde Enerji",
        "Kimyasal Tepkimelerde Hız", "Kimyasal Denge", "Asit-Baz Dengesi",
        "KÇÇ (Çözünürlük Dengesi)", "Kimya ve Elektrik", "Karbon Kimyasına Giriş",
        "Organik Kimya"
    ],
    "BİYOLOJİ": [
        "Yaşam Bilimi Biyoloji", "Hücre ve Organeller", "Canlıların Sınıflandırılması",
        "Hücre Bölünmeleri (Mitoz / Mayoz)", "Kalıtım", "Ekosistem Ekolojisi",
        "İnsan Fizyolojisi (Sistemler)", "Göz ve Duyu Organları", "Nükleik Asitler ve Protein Sentezi",
        "Hücresel Solunum ve Fotosentez / Kemosentez", "Bitki Biyolojisi", "Canlılar ve Çevre"
    ],
    "TARİH": [
        "Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya",
        "İlk ve Orta Çağlarda Türk Dünyası", "İslam Medeniyetinin Doğuşu",
        "İlk Türk İslam Devletleri", "Yerleşme ve Devletleşme Sürecinde Selçuklu Türkiye'si",
        "Beylikten Devlete Osmanlı Siyaseti", "Devletleşme Sürecinde Savaşçılar ve Askerler",
        "Beylikten Devlete Osmanlı Medeniyeti", "Dünya Gücü Osmanlı (1453-1595)",
        "Değişim Çağında Avrupa ve Osmanlı", "Uluslararası İlişkilerde Denge Stratejisi (1774-1914)",
        "Devrimler Çağında Değişen Devlet-Toplum İlişkileri", "Sermaye ve Emek",
        "XIX. ve XX. Yüzyılda Değişen Gündelik Hayat", "20. Yüzyıl Başlarında Osmanlı Devleti ve Dünya",
        "Milli Mücadele", "Atatürkçülük ve Türk İnkılabı", "İki Dünya Savaşı Arasındaki Dönem",
        "II. Dünya Savaşı", "Soğuk Savaş Dönemi", "Yumuşama Dönemi", "Küreselleşen Dünya"
    ],
    "COĞRAFYA": [
        "Doğa ve İnsan", "Dünya'nın Şekli ve Hareketleri", "Coğrafi Konum", "Harita Bilgisi",
        "Atmosfer ve İklim", "Sıcaklık / Basınç / Rüzgarlar / Nem ve Yağış", "İklim Tipleri",
        "İç ve Dış Kuvvetler", "Türkiye'nin Yer Şekilleri", "Nüfus ve Yerleşme",
        "Ekonomik Faaliyetler", "Bölgeler ve Ülkeler", "Doğal Afetler", "Ekosistem ve Biyoçeşitlilik",
        "Şehirlerin Fonksiyonları", "Türkiye'de Tarım, Hayvancılık ve Sanayi", "Küresel Ticaret ve Turizm"
    ],
    "FELSEFE": [
        "Felsefeyi Tanıma", "Felsefe ile Düşünme", "Varlık Felsefesi (Ontoloji)",
        "Bilgi Felsefesi (Epistemoloji)", "Bilim Felsefesi", "Ahlak Felsefesi (Etik)",
        "Siyaset Felsefesi", "Sanat Felsefesi (Estetik)", "Din Felsefesi", "Felsefi Okuma ve Yazma"
    ],
    "DİN KÜLTÜRÜ": [
        "Bilgi ve İnanç", "Din ve İslam", "İslam ve İbadet", "Gençlik ve Değerler",
        "Gönül Coğrafyamız", "Allah İnsan İlişkisi", "Dünya ve Ahiret", "Kur'an'a Göre Hz. Muhammed",
        "İslam Düşüncesinde Yorumlar (Mezhepler)"
    ]
}


def get_default_user_data():
    tracking = {}
    for c, topics in DEFAULT_COURSES.items():
        tracking[c] = {}
        for t in topics:
            tracking[c][t] = {"konu": False, "soru": False, "tekrar": False, "note": ""}
    return {
        "tracking": tracking,
        "daily_logs": {},  # "YYYY-MM-DD": {"solved": 0, "study_time": 0, "target": 100, "target_time": 120}
        "schedules": {},   # "YYYY-MM-DD": [{"id": 1, "task": "...", "done": False, "photo": "..."}]
        "notes": []        # [{"id": 1, "title": "...", "content": "...", "date": "..."}]
    }


def load_user_data(username):
    filepath = get_user_data_file(username)
    if not os.path.exists(filepath):
        data = get_default_user_data()
        save_user_data(username, data)
        return data
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_data = get_default_user_data()
            # Yeni eklenen ders/konuları eksiksiz senkronize et
            for c, topics in default_data["tracking"].items():
                if c not in data["tracking"]:
                    data["tracking"][c] = topics
                else:
                    for t, sub in topics.items():
                        if t not in data["tracking"][c]:
                            data["tracking"][c][t] = sub
            if "daily_logs" not in data:
                data["daily_logs"] = {}
            if "schedules" not in data:
                data["schedules"] = {}
            if "notes" not in data:
                data["notes"] = []
            return data
    except Exception:
        return get_default_user_data()


def save_user_data(username, data):
    filepath = get_user_data_file(username)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- ORTAK HTML ŞABLONU ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sınav & Ders Takip Platformu</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #50e3c2;
            --bg-color: #f4f7f6;
            --card-bg: #ffffff;
            --text-color: #333333;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar-brand { font-weight: bold; font-size: 1.4rem; }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .card-header {
            background-color: var(--card-bg);
            border-bottom: 1px solid #edf2f7;
            font-weight: 600;
        }
        .btn-primary { background-color: var(--primary-color); border: none; }
        .btn-primary:hover { background-color: #357abd; }
        .progress { height: 10px; border-radius: 5px; }
        .status-badge { font-size: 0.8rem; padding: 4px 8px; border-radius: 4px; }
        .stat-card {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border-radius: 12px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}"><i class="fa-solid fa-graduation-cap me-2"></i>DersTakip</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                {% if session.get('user') %}
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}"><i class="fa-solid fa-chart-line me-1"></i> Panel</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('tracking') }}"><i class="fa-solid fa-book-open me-1"></i> Konu Takibi</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('daily_log') }}"><i class="fa-solid fa-check-double me-1"></i> Günlük Soru / Süre</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('schedule') }}"><i class="fa-solid fa-calendar-days me-1"></i> Takvim & Program</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('notes') }}"><i class="fa-solid fa-note-sticky me-1"></i> Notlarım</a></li>
                </ul>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><span class="nav-link text-light"><i class="fa-solid fa-user me-1"></i> {{ session['user'] }}</span></li>
                    <li class="nav-item"><a class="nav-link text-danger" href="{{ url_for('logout') }}"><i class="fa-solid fa-right-from-bracket me-1"></i> Çıkış</a></li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# --- ROTALAR / YÖNLENDİRMELER ---

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        users = load_users()
        if username in users and users[username] == password:
            session["user"] = username
            flash("Başarıyla giriş yapıldı!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Hatalı kullanıcı adı veya şifre!", "danger")

    login_html = """
    {% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5">
        <div class="col-md-4">
            <div class="card p-4">
                <h3 class="text-center mb-4">Giriş Yap</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Kullanıcı Adı</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Şifre</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Giriş</button>
                </form>
                <div class="mt-3 text-center">
                    <a href="{{ url_for('register') }}">Hesabın yok mu? Kayıt Ol</a>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", login_html))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        users = load_users()

        if username in users:
            flash("Bu kullanıcı adı zaten alınmış!", "warning")
        elif not username or not password:
            flash("Lütfen tüm alanları doldurun!", "warning")
        else:
            users[username] = password
            save_users(users)
            load_user_data(username)  # Varsayılan json yapısını oluştur
            flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.", "success")
            return redirect(url_for("login"))

    reg_html = """
    {% extends "base" %}
    {% block content %}
    <div class="row justify-content-center mt-5">
        <div class="col-md-4">
            <div class="card p-4">
                <h3 class="text-center mb-4">Kayıt Ol</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Kullanıcı Adı</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Şifre</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">Kayıt Ol</button>
                </form>
                <div class="mt-3 text-center">
                    <a href="{{ url_for('login') }}">Zaten hesabın var mı? Giriş Yap</a>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", reg_html))


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Oturum kapatıldı.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    tracking = user_data.get("tracking", {})

    # Genel Tamamlanma Oranları
    course_stats = {}
    total_topics = 0
    completed_topics = 0

    for course, topics in tracking.items():
        c_total = len(topics)
        c_done = sum(1 for t, val in topics.items() if val.get("konu") and val.get("soru"))
        percent = int((c_done / c_total) * 100) if c_total > 0 else 0
        course_stats[course] = {"total": c_total, "done": c_done, "percent": percent}

        total_topics += c_total
        completed_topics += c_done

    overall_percent = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

    # Günlük Soru İstatistikleri Grafik Verisi (Son 7 Gün)
    today = date.today()
    last_7_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    chart_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%d %b") for d in last_7_days]
    chart_questions = [user_data.get("daily_logs", {}).get(d, {}).get("solved", 0) for d in last_7_days]
    chart_times = [user_data.get("daily_logs", {}).get(d, {}).get("study_time", 0) for d in last_7_days]

    dash_html = f"""
    <div class="row">
        <div class="col-md-4">
            <div class="stat-card mb-4 text-center">
                <h2>%{overall_percent}</h2>
                <p class="mb-0">Genel Müfredat Tamamlanma Oranı</p>
                <small>{completed_topics} / {total_topics} Konu Bitti</small>
            </div>
        </div>
        <div class="col-md-8">
            <div class="card p-3">
                <h5>Son 7 Günlük Soru / Süre Grafiği</h5>
                <canvas id="weeklyChart" height="100"></canvas>
            </div>
        </div>
    </div>

    <h4 class="mt-4 mb-3">Ders Bazlı İlerleme</h4>
    <div class="row">
        {% for course, stat in course_stats.items() %}
        <div class="col-md-4">
            <div class="card p-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0 fw-bold">{{ course }}</h6>
                    <span class="badge bg-primary">%{ stat.percent }</span>
                </div>
                <div class="progress">
                    <div class="progress-bar bg-success" style="width: {{ stat.percent }}%"></div>
                </div>
                <small class="text-muted mt-2 d-block">{{ stat.done }} / {{ stat.total }} Konu Tamamlandı</small>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        const ctx = document.getElementById('weeklyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [
                    {{
                        label: 'Çözülen Soru',
                        data: {json.dumps(chart_questions)},
                        borderColor: '#4a90e2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        fill: true,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Çalışma Süresi (Dakika)',
                        data: {json.dumps(chart_times)},
                        borderColor: '#50e3c2',
                        backgroundColor: 'rgba(80, 227, 194, 0.1)',
                        fill: true,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                scales: {{
                    y: {{ type: 'linear', position: 'left' }},
                    y1: {{ type: 'linear', position: 'right', grid: {{ drawOnChartArea: false }} }}
                }}
            }}
        }});
    </script>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", dash_html),
        course_stats=course_stats
    )


@app.route("/tracking", methods=["GET", "POST"])
def tracking():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])

    if request.method == "POST":
        # Form güncellemelerini kaydet
        for course, topics in user_data["tracking"].items():
            for topic in topics.keys():
                k_key = f"konu_{course}_{topic}"
                s_key = f"soru_{course}_{topic}"
                t_key = f"tekrar_{course}_{topic}"
                n_key = f"note_{course}_{topic}"

                user_data["tracking"][course][topic]["konu"] = k_key in request.form
                user_data["tracking"][course][topic]["soru"] = s_key in request.form
                user_data["tracking"][course][topic]["tekrar"] = t_key in request.form
                user_data["tracking"][course][topic]["note"] = request.form.get(n_key, "")

        save_user_data(session["user"], user_data)
        flash("İlerlemeleriniz başarıyla kaydedildi!", "success")
        return redirect(url_for("tracking"))

    selected_course = request.args.get("course", list(DEFAULT_COURSES.keys())[0])

    track_html = """
    <div class="card p-3 mb-4">
        <div class="d-flex flex-wrap gap-2">
            {% for c in courses %}
                <a href="{{ url_for('tracking', course=c) }}" class="btn btn-outline-primary {% if c == selected_course %}active{% endif %}">
                    {{ c }}
                </a>
            {% endfor %}
        </div>
    </div>

    <form method="POST">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">{{ selected_course }} Konu Listesi</h5>
                <button type="submit" class="btn btn-success"><i class="fa-solid fa-floppy-disk me-1"></i> Değişiklikleri Kaydet</button>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Konu Adı</th>
                                <th class="text-center">Konu Anlatımı</th>
                                <th class="text-center">Soru Çözümü</th>
                                <th class="text-center">Tekrar Yapıldı</th>
                                <th>Özel Not</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for topic, data in tracking[selected_course].items() %}
                            <tr>
                                <td><strong>{{ topic }}</strong></td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="konu_{{selected_course}}_{{topic}}" {% if data.konu %}checked{% endif %}>
                                </td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="soru_{{selected_course}}_{{topic}}" {% if data.soru %}checked{% endif %}>
                                </td>
                                <td class="text-center">
                                    <input type="checkbox" class="form-check-input" name="tekrar_{{selected_course}}_{{topic}}" {% if data.tekrar %}checked{% endif %}>
                                </td>
                                <td>
                                    <input type="text" class="form-control form-control-sm" name="note_{{selected_course}}_{{topic}}" value="{{ data.note }}" placeholder="Not ekle...">
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </form>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", track_html),
        courses=list(DEFAULT_COURSES.keys()),
        selected_course=selected_course,
        tracking=user_data["tracking"]
    )


@app.route("/daily_log", methods=["GET", "POST"])
def daily_log():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    selected_date = request.args.get("date", date.today().strftime("%Y-%m-%d"))

    if request.method == "POST":
        solved = int(request.form.get("solved", 0))
        study_time = int(request.form.get("study_time", 0))
        target = int(request.form.get("target", 100))
        target_time = int(request.form.get("target_time", 120))

        if "daily_logs" not in user_data:
            user_data["daily_logs"] = {}

        user_data["daily_logs"][selected_date] = {
            "solved": solved,
            "study_time": study_time,
            "target": target,
            "target_time": target_time
        }

        save_user_data(session["user"], user_data)
        flash("Günlük veriler kaydedildi!", "success")
        return redirect(url_for("daily_log", date=selected_date))

    log_data = user_data.get("daily_logs", {}).get(selected_date, {
        "solved": 0, "study_time": 0, "target": 100, "target_time": 120
    })

    log_html = """
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4">
                <h4>Günlük Çalışma & Soru Kaydı</h4>
                <form method="GET" class="mb-4">
                    <label class="form-label">Tarih Seç</label>
                    <input type="date" name="date" class="form-control" value="{{ selected_date }}" onchange="this.form.submit()">
                </form>
                <hr>
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Çözülen Soru</label>
                            <input type="number" name="solved" class="form-control" value="{{ log_data.solved }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Hedef Soru</label>
                            <input type="number" name="target" class="form-control" value="{{ log_data.target }}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Çalışma Süresi (Dk)</label>
                            <input type="number" name="study_time" class="form-control" value="{{ log_data.study_time }}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Hedef Süre (Dk)</label>
                            <input type="number" name="target_time" class="form-control" value="{{ log_data.target_time }}">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Kaydet</button>
                </form>
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", log_html),
        selected_date=selected_date,
        log_data=log_data
    )


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])
    selected_date = request.args.get("date", date.today().strftime("%Y-%m-%d"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            task = request.form.get("task")
            file = request.files.get("photo")
            filename = ""

            if file and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                filename = f"{session['user']}_{int(datetime.now().timestamp())}_{fname}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            if selected_date not in user_data["schedules"]:
                user_data["schedules"][selected_date] = []

            user_data["schedules"][selected_date].append({
                "id": int(datetime.now().timestamp() * 1000),
                "task": task,
                "done": False,
                "photo": filename
            })

        elif action == "toggle":
            task_id = int(request.form.get("task_id"))
            for t in user_data["schedules"].get(selected_date, []):
                if t["id"] == task_id:
                    t["done"] = not t["done"]

        elif action == "delete":
            task_id = int(request.form.get("task_id"))
            user_data["schedules"][selected_date] = [
                t for t in user_data["schedules"].get(selected_date, []) if t["id"] != task_id
            ]

        save_user_data(session["user"], user_data)
        return redirect(url_for("schedule", date=selected_date))

    tasks = user_data.get("schedules", {}).get(selected_date, [])

    sch_html = """
    <div class="row">
        <div class="col-md-5">
            <div class="card p-3">
                <h5>Tarih Seçin</h5>
                <form method="GET">
                    <input type="date" name="date" class="form-control mb-3" value="{{ selected_date }}" onchange="this.form.submit()">
                </form>
                <hr>
                <h6>Yeni Görev / Program Ekle</h6>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="add">
                    <div class="mb-3">
                        <input type="text" name="task" class="form-control" placeholder="Örn: 2 Saat Matematik Çözülecek" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Soru Fotoğrafı / Ek (Opsiyonel)</label>
                        <input type="file" name="photo" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Ekle</button>
                </form>
            </div>
        </div>

        <div class="col-md-7">
            <div class="card p-3">
                <h5>{{ selected_date }} Tarihindeki Programım</h5>
                {% if tasks %}
                    <ul class="list-group list-group-flush">
                        {% for t in tasks %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <div>
                                    <form method="POST" style="display:inline;">
                                        <input type="hidden" name="action" value="toggle">
                                        <input type="hidden" name="task_id" value="{{ t.id }}">
                                        <button type="submit" class="btn btn-sm {% if t.done %}btn-success{% else %}btn-outline-secondary{% endif %} me-2">
                                            <i class="fa-solid fa-check"></i>
                                        </button>
                                    </form>
                                    <span style="{% if t.done %}text-decoration: line-through; color: gray;{% endif %}">
                                        {{ t.task }}
                                    </span>
                                    {% if t.photo %}
                                        <br>
                                        <a href="{{ url_for('uploaded_file', filename=t.photo) }}" target="_blank" class="badge bg-info text-decoration-none mt-1">
                                            <i class="fa-solid fa-image"></i> Fotoğrafı Gör
                                        </a>
                                    {% endif %}
                                </div>
                                <form method="POST">
                                    <input type="hidden" name="action" value="delete">
                                    <input type="hidden" name="task_id" value="{{ t.id }}">
                                    <button type="submit" class="btn btn-sm btn-danger"><i class="fa-solid fa-trash"></i></button>
                                </form>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted mt-2">Bu tarihe ait program eklenmemiş.</p>
                {% endif %}
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", sch_html),
        selected_date=selected_date,
        tasks=tasks
    )


@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user" not in session:
        return redirect(url_for("login"))

    user_data = load_user_data(session["user"])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            title = request.form.get("title")
            content = request.form.get("content")
            user_data["notes"].append({
                "id": int(datetime.now().timestamp() * 1000),
                "title": title,
                "content": content,
                "date": date.today().strftime("%Y-%m-%d")
            })

        elif action == "delete":
            note_id = int(request.form.get("note_id"))
            user_data["notes"] = [n for n in user_data["notes"] if n["id"] != note_id]

        save_user_data(session["user"], user_data)
        return redirect(url_for("notes"))

    notes_html = """
    <div class="row">
        <div class="col-md-4">
            <div class="card p-3">
                <h5>Yeni Not Ekle</h5>
                <form method="POST">
                    <input type="hidden" name="action" value="add">
                    <div class="mb-3">
                        <input type="text" name="title" class="form-control" placeholder="Başlık" required>
                    </div>
                    <div class="mb-3">
                        <textarea name="content" class="form-control" rows="5" placeholder="Not detayları..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Kaydet</button>
                </form>
            </div>
        </div>

        <div class="col-md-8">
            <div class="row">
                {% for n in notes_list %}
                <div class="col-md-6">
                    <div class="card p-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title">{{ n.title }}</h5>
                            <form method="POST">
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="note_id" value="{{ n.id }}">
                                <button type="submit" class="btn btn-sm btn-outline-danger"><i class="fa-solid fa-trash"></i></button>
                            </form>
                        </div>
                        <p class="card-text mt-2" style="white-space: pre-wrap;">{{ n.content }}</p>
                        <small class="text-muted text-end d-block">{{ n.date }}</small>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    """
    return render_template_string(
        BASE_HTML.replace("{% block content %}{% endblock %}", notes_html),
        notes_list=user_data.get("notes", [])
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --- UYGULAMA BAŞLATMA VE PORT DÜZENLEMESİ (RENDER UYUMLU) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
