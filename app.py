import copy
import json
import os
import time
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    send_from_directory,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "mustafa_berk_gizli_anahtar_123"

UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "user_data"
USERS_FILE = "users.json"

for folder in [UPLOAD_FOLDER, DATA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Varsayılan Kullanıcı Kadrosu
VARSAYILAN_USERS = {
    "admin": {"sifre": "admin123", "rol": "admin", "ad": "Yönetici / Koç"},
    "mustafa": {"sifre": "1234", "rol": "ogrenci", "ad": "Mustafa Berk"},
    "ahmet": {"sifre": "1234", "rol": "ogrenci", "ad": "Ahmet Yılmaz"},
    "ayse": {"sifre": "1234", "rol": "ogrenci", "ad": "Ayşe Kaya"},
}


def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(VARSAYILAN_USERS, f, ensure_ascii=False, indent=2)
    return VARSAYILAN_USERS


def kullanicilari_kaydet(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)


VARSAYILAN_PROGRAM = {
    "Pazartesi": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:272-275 | Prf S:153-154",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj tyt S:160-165",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: elektrostatik",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:148-156",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: plm S:179-188",
            "tamamlandi": False,
        },
        {"baslik": "5. Etüt Türkçe", "detay": "Konu: S:", "tamamlandi": False},
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: S:",
            "tamamlandi": False,
        },
        {"baslik": "Geometri", "detay": "Konu: S:", "tamamlandi": False},
        {"baslik": "Sosyal", "detay": "Konu: S:", "tamamlandi": False},
    ],
    "Salı": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:247-250 | Prf S:155-156",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:8-13",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:162-169",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:157-162 + Mol konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: plm S:189-190 | Prf S:157-164",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: 345 S:210-214",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:63-68",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:67-72",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Çarşamba": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:252-255 | Prf S:157-158",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:14-19",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:170-179",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: Aydın fasikül S:26-45 + Mol konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:165-174",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:224-231",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:69-74",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:73-78",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Perşembe": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:256-259 | Prf S:159-160",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:20-23 + tara",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:180-183 | bil.sar S:147-150",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: Aydın fasikül S:46-50 | Plm S:164-169",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:175-184",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:232-237",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:75-80",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: Açıortay S:kenarortay konu",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Cuma": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:260-263 | Prf S:161-162",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:87-94",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: bil.sar tyt S:151-160",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm S:170-179",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:185-190 + tara",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: bil.sar S:deneme 8 (5-6)",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:81-86",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:79-84",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:4. video",
            "tamamlandi": False,
        },
    ],
    "Cumartesi": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:264-267 | Prf S:163-164",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:95-102",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: elk akım S:konu",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: kimyasal tepkimeler ve hesaplamalar konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:193-198 + tara Kalıtım konu",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:238-243",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: rasyonel tyt S:deneme 2",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:85-90",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:6. video",
            "tamamlandi": False,
        },
    ],
    "Pazar": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:268-271 | Prf S:165-166",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:103-110",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:184-191",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:59-89 testler",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: kalıtım S:konu",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Matris tyt (T: M: F: S: Toplam:)",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: S:",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:91-96",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:7. video",
            "tamamlandi": False,
        },
    ],
}


def kullanici_dosya_yolu(username):
    return os.path.join(DATA_FOLDER, f"data_{username}.json")


def verileri_oku(username):
    filepath = kullanici_dosya_yolu(username)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("sorular", [])
                data.setdefault("notlar", [])
                data.setdefault("denemeler", [])
                data.setdefault("gunluk_sureler", {})
                # VARSAYILAN_PROGRAM kopyasını atıyoruz
                data.setdefault("program", copy.deepcopy(VARSAYILAN_PROGRAM))
                data.setdefault("resim", "")
                return data
        except Exception:
            pass
    # Yeni kullanıcı oluşturulurken bağımsız derin kopya oluşturuyoruz
    return {
        "resim": "",
        "program": copy.deepcopy(VARSAYILAN_PROGRAM),
        "sorular": [],
        "notlar": [],
        "denemeler": [],
        "gunluk_sureler": {},
    }


def verileri_kaydet(username, data):
    filepath = kullanici_dosya_yolu(username)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_aktif_kullanici():
    users = kullanicilari_yukle()
    if "user" not in session or session["user"] not in users:
        return None
    session_user = session["user"]
    if users[session_user]["rol"] == "admin":
        view_u = request.args.get("view_user") or session.get("view_user")
        if view_u and view_u in users:
            return view_u
        for u, u_data in users.items():
            if u_data.get("rol") == "ogrenci":
                return u
    return session_user


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Çalışma Paneli - Giriş</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
  body { background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .login-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
  .form-control { background-color: #0f172a; border-color: #334155; color: #f8fafc; }
  .form-control:focus { background-color: #0f172a; border-color: #38bdf8; color: #f8fafc; box-shadow: none; }
  .btn-primary { background-color: #0284c7; border-color: #0284c7; font-weight: 700; }
  .btn-primary:hover { background-color: #0369a1; }
</style>
</head>
<body>
<div class="login-card">
  <h4 class="text-center fw-bold text-info mb-4">📚 Çalışma Paneli</h4>
  {% if hata %}
    <div class="alert alert-danger p-2 text-center small mb-3">{{ hata }}</div>
  {% endif %}
  <form method="POST" action="/login">
    <div class="mb-3">
      <label class="form-label small fw-bold text-secondary">Kullanıcı Adı</label>
      <input type="text" name="username" class="form-control" placeholder="Kullanıcı adınızı girin" required>
    </div>
    <div class="mb-4">
      <label class="form-label small fw-bold text-secondary">Şifre</label>
      <input type="password" name="password" class="form-control" placeholder="Şifrenizi girin" required>
    </div>
    <button type="submit" class="btn btn-primary w-100 py-2">Giriş Yap</button>
  </form>
</div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ aktif_ad }} - Çalışma Paneli</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body, body.theme-blue {
  --bg-main: #0f172a;
  --bg-card: #1e293b;
  --bg-inner: #0f172a;
  --border-color: #334155;
  --accent-color: #38bdf8;
  --accent-hover: #0284c7;
  --text-main: #f8fafc;
  --text-sub: #94a3b8;
  --day-btn-bg: linear-gradient(135deg, #1e293b, #0f172a);
}

body.theme-purple {
  --bg-main: #130a2a;
  --bg-card: #211242;
  --bg-inner: #0b051b;
  --border-color: #4c2885;
  --accent-color: #c084fc;
  --accent-hover: #9333ea;
  --text-main: #faf5ff;
  --text-sub: #c084fc;
  --day-btn-bg: linear-gradient(135deg, #211242, #0b051b);
}

body.theme-green {
  --bg-main: #022c22;
  --bg-card: #064e3b;
  --bg-inner: #022c22;
  --border-color: #047857;
  --accent-color: #34d399;
  --accent-hover: #059669;
  --text-main: #ecfdf5;
  --text-sub: #6ee7b7;
  --day-btn-bg: linear-gradient(135deg, #064e3b, #022c22);
}

body.theme-amber {
  --bg-main: #1c100b;
  --bg-card: #2e1a12;
  --bg-inner: #150b07;
  --border-color: #5c3321;
  --accent-color: #fb923c;
  --accent-hover: #ea580c;
  --text-main: #fff7ed;
  --text-sub: #fdba74;
  --day-btn-bg: linear-gradient(135deg, #2e1a12, #150b07);
}

body {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  overflow-x: hidden;
  padding-bottom: 30px;
  transition: all 0.3s ease;
}

.admin-bar {
  background-color: var(--bg-card);
  border-bottom: 2px solid var(--accent-color);
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.nav-container { display: flex; gap: 6px; padding: 10px; background-color: var(--bg-main); position: sticky; top: 0; z-index: 1000; overflow-x: auto; border-bottom: 1px solid var(--border-color); }
.custom-tab-btn { flex: 1; min-width: 80px; background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 4px; text-align: center; color: var(--text-sub); font-weight: 700; font-size: 0.78rem; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; }
.custom-tab-btn.active { background-color: var(--bg-inner); color: var(--accent-color); border-color: var(--accent-color); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); }

.tab-content-container { padding: 0 10px; }
.tab-pane-custom { display: none; }
.tab-pane-custom.active { display: block; }

.card-dark { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
.day-btn { background: var(--day-btn-bg); border: 1px solid var(--border-color); color: var(--text-main); width: 100%; text-align: left; padding: 14px 18px; border-radius: 10px; font-weight: 700; font-size: 1.05rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; margin-bottom: 10px; }
.progress-badge { font-size: 0.85rem; padding: 4px 10px; border-radius: 20px; background-color: var(--bg-inner); color: var(--accent-color); border: 1px solid var(--border-color); font-weight: 700; }
.time-badge { font-size: 0.82rem; padding: 3px 8px; border-radius: 6px; background-color: rgba(56, 189, 248, 0.15); color: var(--accent-color); margin-left: 8px; border: 1px solid var(--border-color); }
.day-content { display: none; padding: 12px; background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; margin-bottom: 15px; }
.etut-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.box { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px; cursor: pointer; position: relative; transition: transform 0.1s ease; }
.box.completed { background-color: #064e3b !important; border-color: #10b981 !important; }
.box-title { font-weight: 700; font-size: 0.88rem; color: var(--text-main); margin-bottom: 4px; }
.box-detay { font-size: 0.75rem; color: var(--text-sub); word-break: break-word; }
.completed .box-title { color: #ffffff !important; }
.completed .box-detay { color: #a7f3d0 !important; }
.edit-btn { position: absolute; top: 6px; right: 6px; font-size: 11px; background: rgba(255, 255, 255, 0.1); border: none; border-radius: 4px; padding: 2px 5px; color: var(--text-sub); }

.timer-box { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; text-align: center; }
.timer-display { font-size: 2.8rem; font-weight: 800; color: var(--accent-color); font-family: monospace; letter-spacing: 2px; background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; padding: 10px; margin-top: 10px; margin-bottom: 15px; }
.form-control, .form-select { background-color: var(--bg-inner); border-color: var(--border-color); color: var(--text-main); }
.form-control:focus, .form-select:focus { background-color: var(--bg-inner); color: var(--text-main); border-color: var(--accent-color); box-shadow: none; }

.palette-container { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; align-items: center; background: var(--bg-card); padding: 10px; border-radius: 12px; border: 1px solid var(--border-color); flex-wrap: wrap; }
.theme-btn { border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 0.8rem; border: 1px solid var(--border-color); cursor: pointer; transition: all 0.2s; }
.theme-btn.btn-blue { background-color: #0f172a; color: #38bdf8; border-color: #38bdf8; }
.theme-btn.btn-purple { background-color: #130a2a; color: #c084fc; border-color: #c084fc; }
.theme-btn.btn-green { background-color: #022c22; color: #34d399; border-color: #34d399; }
.theme-btn.btn-amber { background-color: #1c100b; color: #fb923c; border-color: #fb923c; }

.question-card { background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; height: 100%; }
.question-img { width: 100%; height: 180px; object-fit: cover; cursor: pointer; }

.note-card { background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; position: relative; }
.note-title { font-weight: 700; font-size: 1rem; color: var(--accent-color); margin-bottom: 6px; }
.note-content { font-size: 0.88rem; color: var(--text-main); white-space: pre-wrap; word-break: break-word; }
.note-date { font-size: 0.7rem; color: var(--text-sub); margin-top: 10px; }

.table-dark-custom { background-color: var(--bg-inner); color: var(--text-main); border-color: var(--border-color); }
.table-dark-custom th { background-color: var(--bg-card); color: var(--accent-color); border-color: var(--border-color); font-size: 0.85rem; text-align: center; white-space: nowrap; }
.table-dark-custom td { border-color: var(--border-color); vertical-align: middle; padding: 4px; min-width: 140px; }
.table-input { background-color: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-main); font-size: 0.78rem; padding: 6px; border-radius: 6px; width: 100%; min-height: 50px; }
.etut-label { font-weight: 700; color: #f8fafc; font-size: 0.82rem; text-align: center; background-color: var(--bg-card); }
</style>
</head>
<body>

<div class="admin-bar">
  <div>
    <span class="fw-bold text-info">👤 {{ session_user_ad }}</span>
    {% if is_admin %}
      <span class="badge bg-warning text-dark ms-2">YÖNETİCİ MODU</span>
    {% endif %}
  </div>

  {% if is_admin %}
  <div class="d-flex align-items-center gap-2">
    <label class="small text-light fw-bold">Öğrenci Seç:</label>
    <select class="form-select form-select-sm" onchange="ogrenciDegistir(this.value)">
      {% for u_id, u_info in tum_ogrenciler.items() %}
        {% if u_info.rol == 'ogrenci' %}
          <option value="{{ u_id }}" {% if u_id == aktif_kullanici %}selected{% endif %}>{{ u_info.ad }}</option>
        {% endif %}
      {% endfor %}
    </select>
  </div>
  {% endif %}

  <a href="/logout" class="btn btn-sm btn-outline-danger font-bold">Çıkış Yap</a>
</div>

<div class="nav-container">
  <div class="custom-tab-btn active" id="btn-prog" onclick="switchTab(0)">📅 Program</div>
  <div class="custom-tab-btn" id="btn-edit" onclick="switchTab(1)">⚙️ Düzenle</div>
  <div class="custom-tab-btn" id="btn-timer" onclick="switchTab(2)">⏱️ Kronometre</div>
  <div class="custom-tab-btn" id="btn-soru" onclick="switchTab(3)">❓ Sorular</div>
  <div class="custom-tab-btn" id="btn-analiz" onclick="switchTab(4)">📊 Deneme Analizi</div>
  <div class="custom-tab-btn" id="btn-not" onclick="switchTab(5)">📝 Notlarım</div>
  {% if is_admin %}
  <div class="custom-tab-btn" id="btn-users" onclick="switchTab(6)">👥 Kullanıcı Yönetimi</div>
  {% endif %}
</div>

<div class="tab-content-container">

<div class="palette-container">
  <small class="fw-bold text-secondary me-2">🎨 Renk Teması Seç:</small>
  <button class="theme-btn btn-blue" onclick="setTheme('theme-blue')">Gece Mavisi</button>
  <button class="theme-btn btn-purple" onclick="setTheme('theme-purple')">Siber Mor</button>
  <button class="theme-btn btn-green" onclick="setTheme('theme-green')">Zümrüt Yeşil</button>
  <button class="theme-btn btn-amber" onclick="setTheme('theme-amber')">Gün Batımı</button>
</div>

<div class="tab-pane-custom active" id="pane-prog">
  <div class="card card-dark p-3 mb-3">
    <label class="fw-bold mb-2 text-light">📸 Program Fotoğrafı Yükle / Değiştir:</label>
    <div class="input-group">
      <input type="file" id="imageInput" class="form-control" accept="image/*">
      <button class="btn btn-primary fw-bold" onclick="uploadNewProgram()">Yükle</button>
    </div>
  </div>

  {% if veriler.resim %}
  <div class="card card-dark p-2 mb-3 text-center">
    <img src="/uploads/{{ veriler.resim }}" class="img-fluid rounded border border-secondary" style="max-height: 300px; object-fit: contain;">
  </div>
  {% endif %}

  <div class="card card-dark p-3">
    <h6 class="fw-bold text-center mb-3 text-light">✨ {{ aktif_ad }} - Güncel Haftalık Programı</h6>
    {% set gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"] %}
    {% for gun in gunler %}
      {% set etutler = veriler.program[gun] %}
      {% set toplam = etutler | length %}
      {% set tamamlanan = etutler | selectattr("tamamlandi", "equalto", true) | list | length %}
      {% set yuzde = (tamamlanan / toplam * 100) | round | int if toplam > 0 else 0 %}
      {% set gun_suresi = veriler.gunluk_sureler.get(gun, "") %}

      <button class="day-btn" onclick="toggleDay('{{ gun }}')">
        <div>
          <span>{{ gun }}</span>
          {% if gun_suresi %}
            <span class="time-badge">⏱️ {{ gun_suresi }}</span>
          {% endif %}
        </div>
        <span class="progress-badge" id="badge-{{ gun }}">%{{ yuzde }} ({{ tamamlanan }}/{{ toplam }})</span>
      </button>

      <div id="day-{{ gun }}" class="day-content">
        <div class="etut-grid">
        {% for row_idx in range(etutler | length) %}
          {% set etut = etutler[row_idx] %}
          <div class="box {% if etut.tamamlandi %}completed{% endif %}" id="box-{{ gun }}-{{ row_idx }}" onclick="toggleEtut('{{ gun }}', {{ row_idx }})">
            <button class="edit-btn" onclick="editEtut(event, '{{ gun }}', {{ row_idx }}, '{{ etut.baslik }}', '{{ etut.detay }}')">✏️</button>
            <div class="box-title" id="title-{{ gun }}-{{ row_idx }}">{{ etut.baslik }}</div>
            <div class="box-detay" id="detay-{{ gun }}-{{ row_idx }}">{{ etut.detay }}</div>
          </div>
        {% endfor %}
        </div>
      </div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-edit">
  <div class="card card-dark p-3 mb-3">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-bold text-light m-0">⚙️ Kağıt Düzeninde Haftalık Program Tablosu ({{ aktif_ad }})</h6>
      <button class="btn btn-sm btn-success fw-bold" onclick="topluKaydet()">💾 Değişiklikleri Kaydet</button>
    </div>

    {% set etut_listesi = veriler.program["Pazartesi"] %}
    <div class="table-responsive">
      <table class="table table-dark-custom table-bordered align-middle m-0">
        <thead>
          <tr>
            <th style="min-width: 140px;" class="text-center bg-dark text-info">Etüt / Ders</th>
            {% for gun in gunler %}
              <th style="min-width: 150px;">{{ gun }}</th>
            {% endfor %}
          </tr>
        </thead>
        <tbody>
          {% for e_idx in range(etut_listesi | length) %}
            <tr>
              <td class="etut-label">
                <input type="text" class="form-control text-center fw-bold bg-dark text-info border-secondary mb-1" id="etut-baslik-row-{{ e_idx }}" value="{{ etut_listesi[e_idx].baslik }}">
              </td>
              {% for gun in gunler %}
                <td>
                  <textarea class="form-control table-input" id="tablo-detay-{{ gun }}-{{ e_idx }}" rows="2">{{ veriler.program[gun][e_idx].detay if e_idx < (veriler.program[gun] | length) else '' }}</textarea>
                </td>
              {% endfor %}
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    <button class="btn btn-success fw-bold mt-3 w-100 py-2" onclick="topluKaydet()">💾 Tüm Tabloyu Kaydet</button>
  </div>
</div>

<div class="tab-pane-custom" id="pane-timer">
  <div class="timer-box">
    <h5 class="fw-bold text-light mb-2">⏱️ Çalışma Kronometresi</h5>
    <div class="timer-display" id="stopwatchDisplay">00:00:00</div>
    <div class="d-flex justify-content-center gap-2 mb-3">
      <button class="btn btn-success fw-bold px-4" onclick="startStopwatch()">Başlat</button>
      <button class="btn btn-warning fw-bold px-4 text-dark" onclick="pauseStopwatch()">Durdur</button>
      <button class="btn btn-danger fw-bold px-4" onclick="resetStopwatch()">Sıfırla</button>
    </div>

    <div class="row g-2 align-items-center justify-content-center pt-3 border-top border-secondary">
      <div class="col-md-6 col-8">
        <select id="kayitGunSelect" class="form-select text-center fw-bold">
          {% for gun in gunler %}
            <option value="{{ gun }}">{{ gun }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-4 col-4">
        <button class="btn btn-info w-100 fw-bold text-dark" onclick="sureyiGuneKaydet()">📌 Güne Kaydet</button>
      </div>
    </div>
  </div>

  <div class="timer-box">
    <h5 class="fw-bold text-light mb-2">⏳ Deneme Geri Sayımı (Dakika)</h5>
    <div class="input-group mb-3">
      <input type="number" id="countdownInput" class="form-control text-center" placeholder="Örn: 135" value="135">
      <button class="btn btn-info fw-bold text-dark" onclick="startCountdown()">Kur & Başlat</button>
    </div>
    <div class="timer-display" id="countdownDisplay">02:15:00</div>
    <div class="d-flex justify-content-center gap-2">
      <button class="btn btn-secondary fw-bold px-4" onclick="stopCountdown()">İptal Et</button>
    </div>
  </div>
</div>

<div class="tab-pane-custom" id="pane-soru">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📌 Yapılamayan Soru Ekle ({{ aktif_ad }})</h6>
    <div class="row g-2">
      <div class="col-md-4">
        <select id="soruDers" class="form-select">
          <option value="Matematik">Matematik</option>
          <option value="Fizik">Fizik</option>
          <option value="Kimya">Kimya</option>
          <option value="Biyoloji">Biyoloji</option>
          <option value="Geometri">Geometri</option>
          <option value="Türkçe">Türkçe</option>
          <option value="Sosyal">Sosyal</option>
        </select>
      </div>
      <div class="col-md-8">
        <input type="text" id="soruNot" class="form-control" placeholder="Not/Sayfa/Soru No (Opsiyonel)">
      </div>
      <div class="col-12 mt-2">
        <input type="file" id="soruFoto" class="form-control" accept="image/*">
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="soruEkle()">Soru Kaydet</button>
      </div>
    </div>
  </div>

  <div class="row g-3">
    {% for soru in veriler.sorular %}
    <div class="col-6 col-md-4" id="soru-card-{{ soru.id }}">
      <div class="question-card p-2 text-center">
        <a href="/uploads/{{ soru.dosya }}" target="_blank">
          <img src="/uploads/{{ soru.dosya }}" class="question-img rounded mb-2">
        </a>
        <span class="badge bg-primary mb-1">{{ soru.ders }}</span>
        <div class="small text-secondary mb-2">{{ soru.not }}</div>
        <button class="btn btn-sm btn-outline-danger w-100" onclick="soruSil('{{ soru.id }}')">Çözüldü / Sil</button>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş yapılmayan soru yok! 🎉</div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-analiz">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📈 Yeni Deneme / Analiz Dosyası Ekle ({{ aktif_ad }})</h6>
    <div class="row g-2">
      <div class="col-md-6">
        <input type="text" id="denemeAdi" class="form-control" placeholder="Deneme Adı (Örn: 3D TYT Deneme 1)">
      </div>
      <div class="col-md-6">
        <input type="text" id="denemeNet" class="form-control" placeholder="Net Bilgisi / Not (Örn: TYT 85.5 Net)">
      </div>
      <div class="col-12 mt-2">
        <label class="text-secondary small mb-1">Fotoğraf veya Belge Seç (PDF, Word, Görsel vs.):</label>
        <input type="file" id="denemeDosya" class="form-control">
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="denemeEkle()">Analizi Kaydet</button>
      </div>
    </div>
  </div>

  <div class="row g-3">
    {% for deneme in veriler.denemeler %}
    <div class="col-12 col-md-6" id="deneme-card-{{ deneme.id }}">
      <div class="note-card">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div class="note-title">{{ deneme.adi }}</div>
          <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="denemeSil('{{ deneme.id }}')">🗑️ Sil</button>
        </div>
        <div class="fw-bold text-light mb-2">🎯 {{ deneme.net }}</div>
        {% if deneme.is_image %}
          <a href="/uploads/{{ deneme.dosya }}" target="_blank">
            <img src="/uploads/{{ deneme.dosya }}" class="img-fluid rounded mb-2 border border-secondary" style="max-height: 200px; width: 100%; object-fit: cover;">
          </a>
        {% else %}
          <div class="p-2 mb-2 bg-dark rounded border border-secondary text-center">
            <a href="/uploads/{{ deneme.dosya }}" target="_blank" class="btn btn-sm btn-outline-info text-decoration-none fw-bold">
              📄 Dosyayı / Analizi Aç ({{ deneme.orj_isim }})
            </a>
          </div>
        {% endif %}
        <div class="note-date">📅 Eklenme Tarihi: {{ deneme.tarih }}</div>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş deneme analizi yok! 📈</div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-not">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📝 Yeni Not Ekle ({{ aktif_ad }})</h6>
    <input type="text" id="notBaslik" class="form-control mb-2" placeholder="Not Başlığı (Örn: Formüller / Hatırlatma)">
    <textarea id="notIcerik" class="form-control mb-3" rows="3" placeholder="Notunu buraya yaz..."></textarea>
    <button class="btn btn-success w-100 fw-bold" onclick="notEkle()">Notu Kaydet</button>
  </div>

  <div class="row g-3">
    {% for not_item in veriler.notlar %}
    <div class="col-12 col-md-6" id="note-card-{{ not_item.id }}">
      <div class="note-card">
        <div class="d-flex justify-content-between align-items-start">
          <div class="note-title">{{ not_item.baslik }}</div>
          <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="notSil('{{ not_item.id }}')">🗑️ Sil</button>
        </div>
        <div class="note-content">{{ not_item.icerik }}</div>
        <div class="note-date">📅 {{ not_item.tarih }}</div>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş bir notun yok! ✍️</div>
    {% endfor %}
  </div>
</div>

{% if is_admin %}
<div class="tab-pane-custom" id="pane-users">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-info mb-3">➕ Yeni Öğrenci / Kullanıcı Ekle</h6>
    <div class="row g-2">
      <div class="col-md-3">
        <input type="text" id="kullaniciKullaniciAdi" class="form-control" placeholder="Kullanıcı Adı (Örn: mehmet)">
      </div>
      <div class="col-md-3">
        <input type="text" id="kullaniciSifre" class="form-control" placeholder="Şifre (Örn: 1234)">
      </div>
      <div class="col-md-4">
        <input type="text" id="kullaniciAdSoyad" class="form-control" placeholder="Ad Soyad (Örn: Mehmet Öz)">
      </div>
      <div class="col-md-2">
        <select id="kullaniciRol" class="form-select">
          <option value="ogrenci">Öğrenci</option>
          <option value="admin">Yönetici</option>
        </select>
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="kullaniciEkle()">Kullanıcıyı Kaydet</button>
      </div>
    </div>
  </div>

  <div class="card card-dark p-3">
    <h6 class="fw-bold text-light mb-3">👥 Mevcut Kullanıcılar ve Şifre Düzenleme</h6>
    <div class="table-responsive">
      <table class="table table-dark-custom align-middle m-0">
        <thead>
          <tr>
            <th>Kullanıcı Adı</th>
            <th>Ad Soyad</th>
            <th>Rol</th>
            <th>Şifre Değiştir</th>
            <th>İşlem</th>
          </tr>
        </thead>
        <tbody>
          {% for u_id, u_info in tum_ogrenciler.items() %}
          <tr>
            <td class="fw-bold text-info">{{ u_id }}</td>
            <td>{{ u_info.ad }}</td>
            <td>
              <span class="badge {% if u_info.rol == 'admin' %}bg-warning text-dark{% else %}bg-primary{% endif %}">
                {{ u_info.rol }}
              </span>
            </td>
            <td>
              <div class="input-group input-group-sm">
                <input type="text" id="sifre-input-{{ u_id }}" class="form-control" value="{{ u_info.sifre }}">
                <button class="btn btn-outline-info" onclick="sifreGuncelle('{{ u_id }}')">Güncelle</button>
              </div>
            </td>
            <td>
              {% if u_id != 'admin' and u_id != session_user_id %}
                <button class="btn btn-sm btn-outline-danger" onclick="kullaniciSil('{{ u_id }}')">🗑️ Sil</button>
              {% else %}
                <span class="text-secondary small">Korumalı</span>
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endif %}

</div>

<script>
function ogrenciDegistir(username) {
  window.location.href = "/?view_user=" + username;
}

function setTheme(themeName) {
  document.body.className = '';
  document.body.classList.add(themeName);
  localStorage.setItem('selectedTheme', themeName);
}

(function loadSavedTheme() {
  let savedTheme = localStorage.getItem('selectedTheme') || 'theme-blue';
  document.body.classList.add(savedTheme);
})();

function switchTab(index) {
  const tabs = ['pane-prog', 'pane-edit', 'pane-timer', 'pane-soru', 'pane-analiz', 'pane-not', 'pane-users'];
  const btns = ['btn-prog', 'btn-edit', 'btn-timer', 'btn-soru', 'btn-analiz', 'btn-not', 'btn-users'];
  tabs.forEach((tab, i) => {
    let tabEl = document.getElementById(tab);
    let btnEl = document.getElementById(btns[i]);
    if (tabEl) tabEl.classList.toggle('active', i === index);
    if (btnEl) btnEl.classList.toggle('active', i === index);
  });
}

function toggleDay(gun) {
  let el = document.getElementById('day-' + gun);
  el.style.display = (el.style.display === "block") ? "none" : "block";
}

async function uploadNewProgram() {
  let input = document.getElementById('imageInput');
  if (input.files.length === 0) return alert("Lütfen bir resim dosyası seçin!");
  let formData = new FormData();
  formData.append('photo', input.files[0]);
  let res = await fetch('/upload_new', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function toggleEtut(gun, index) {
  let res = await fetch('/toggle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, index: index})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`box-${gun}-${index}`).classList.toggle('completed', data.yeni_durum);
    document.getElementById(`badge-${gun}`).innerText = `%${data.yuzde} (${data.tamamlanan}/${data.toplam})`;
  }
}

async function editEtut(event, gun, index, mevBaslik, mevDetay) {
  event.stopPropagation();
  let yBaslik = prompt("Ders/Etüt Adı:", mevBaslik);
  if (yBaslik === null) return;
  let yDetay = prompt("Sayfa / Soru Detayı:", mevDetay);
  if (yDetay === null) return;

  let res = await fetch('/edit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, index: index, baslik: yBaslik, detay: yDetay})
  });
  let data = await res.json();
  if (data.success) location.reload();
}

async function topluKaydet() {
  let yeniProgram = {};
  const gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];

  gunler.forEach(gun => {
    yeniProgram[gun] = [];
  });

  let eIdx = 0;
  while (true) {
    let baslikEl = document.getElementById(`etut-baslik-row-${eIdx}`);
    if (!baslikEl) break;
    let baslikVal = baslikEl.value;

    gunler.forEach(gun => {
      let detayEl = document.getElementById(`tablo-detay-${gun}-${eIdx}`);
      let detayVal = detayEl ? detayEl.value : "";
      yeniProgram[gun].push({
        baslik: baslikVal,
        detay: detayVal
      });
    });
    eIdx++;
  }

  let res = await fetch('/toplu_edit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({program: yeniProgram})
  });
  let data = await res.json();
  if (data.success) {
    alert("Program başarıyla güncellendi!");
    location.reload();
  }
}

async function sureyiGuneKaydet() {
  let gun = document.getElementById('kayitGunSelect').value;
  let sure = document.getElementById('stopwatchDisplay').innerText;

  if (sure === "00:00:00") {
    return alert("Henüz bir süre kaydetmediniz!");
  }

  let res = await fetch('/sure_kaydet', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, sure: sure})
  });
  let data = await res.json();
  if (data.success) {
    alert(`${gun} günü için çalışma süresi (${sure}) kaydedildi!`);
    location.reload();
  }
}

async function soruEkle() {
  let foto = document.getElementById('soruFoto').files[0];
  let ders = document.getElementById('soruDers').value;
  let not = document.getElementById('soruNot').value;

  if (!foto) return alert("Lütfen sorunun fotoğrafını seçin!");

  let formData = new FormData();
  formData.append('foto', foto);
  formData.append('ders', ders);
  formData.append('not', not);

  let res = await fetch('/soru_ekle', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function soruSil(soruId) {
  if (!confirm("Bu soruyu silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/soru_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: soruId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`soru-card-${soruId}`).remove();
  }
}

async function denemeEkle() {
  let adi = document.getElementById('denemeAdi').value.trim();
  let net = document.getElementById('denemeNet').value.trim();
  let dosya = document.getElementById('denemeDosya').files[0];

  if (!adi) return alert("Lütfen deneme adını girin!");

  let formData = new FormData();
  formData.append('adi', adi);
  formData.append('net', net);
  if (dosya) formData.append('dosya', dosya);

  let res = await fetch('/deneme_ekle', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function denemeSil(denemeId) {
  if (!confirm("Bu deneme analizini silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/deneme_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: denemeId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`deneme-card-${denemeId}`).remove();
  }
}

async function notEkle() {
  let baslik = document.getElementById('notBaslik').value.trim();
  let icerik = document.getElementById('notIcerik').value.trim();

  if (!baslik || !icerik) return alert("Lütfen hem başlığı hem de not içeriğini girin!");

  let res = await fetch('/not_ekle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({baslik: baslik, icerik: icerik})
  });
  let data = await res.json();
  if (data.success) location.reload();
}

async function notSil(notId) {
  if (!confirm("Bu notu silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/not_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: notId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`note-card-${notId}`).remove();
  }
}

async function kullaniciEkle() {
  let username = document.getElementById('kullaniciKullaniciAdi').value.trim();
  let password = document.getElementById('kullaniciSifre').value.trim();
  let fullname = document.getElementById('kullaniciAdSoyad').value.trim();
  let role = document.getElementById('kullaniciRol').value;

  if (!username || !password || !fullname) return alert("Lütfen tüm alanları doldurun!");

  let res = await fetch('/kullanici_ekle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: username, password: password, fullname: fullname, role: role})
  });
  let data = await res.json();
  if (data.success) {
    alert("Kullanıcı başarıyla eklendi!");
    location.reload();
  } else {
    alert(data.message || "Hata oluştu!");
  }
}

async function sifreGuncelle(targetUsername) {
  let newPassword = document.getElementById(`sifre-input-${targetUsername}`).value.trim();
  if (!newPassword) return alert("Şifre boş olamaz!");

  let res = await fetch('/sifre_guncelle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: targetUsername, new_password: newPassword})
  });
  let data = await res.json();
  if (data.success) {
    alert(`${targetUsername} kullanıcısının şifresi güncellendi!`);
  } else {
    alert("Şifre güncellenemedi!");
  }
}

async function kullaniciSil(targetUsername) {
  if (!confirm(`${targetUsername} kullanıcısını ve verilerini silmek istediğinize emin misiniz?`)) return;

  let res = await fetch('/kullanici_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: targetUsername})
  });
  let data = await res.json();
  if (data.success) {
    alert("Kullanıcı silindi!");
    location.reload();
  } else {
    alert(data.message || "Silme işlemi başarısız!");
  }
}

let swSeconds = 0, swInterval = null;
function startStopwatch() {
  if (swInterval) return;
  swInterval = setInterval(() => {
    swSeconds++;
    let hrs = Math.floor(swSeconds / 3600).toString().padStart(2, '0');
    let mins = Math.floor((swSeconds % 3600) / 60).toString().padStart(2, '0');
    let secs = (swSeconds % 60).toString().padStart(2, '0');
    document.getElementById('stopwatchDisplay').innerText = `${hrs}:${mins}:${secs}`;
  }, 1000);
}
function pauseStopwatch() { clearInterval(swInterval); swInterval = null; }
function resetStopwatch() { pauseStopwatch(); swSeconds = 0; document.getElementById('stopwatchDisplay').innerText = "00:00:00"; }

let cdSeconds = 135 * 60, cdInterval = null;
function startCountdown() {
  stopCountdown();
  let minsVal = parseInt(document.getElementById('countdownInput').value);
  if (isNaN(minsVal) || minsVal <= 0) return alert("Geçerli bir dakika gir!");
  cdSeconds = minsVal * 60;

  cdInterval = setInterval(() => {
    if (cdSeconds <= 0) {
      clearInterval(cdInterval);
      alert("Süre bitti!");
      return;
    }
    cdSeconds--;
    let hrs = Math.floor(cdSeconds / 3600).toString().padStart(2, '0');
    let mins = Math.floor((cdSeconds % 3600) / 60).toString().padStart(2, '0');
    let secs = (cdSeconds % 60).toString().padStart(2, '0');
    document.getElementById('countdownDisplay').innerText = `${hrs}:${mins}:${secs}`;
  }, 1000);
}
function stopCountdown() { clearInterval(cdInterval); cdInterval = null; }
</script>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    users = kullanicilari_yukle()
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if username in users and users[username]["sifre"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        return render_template_string(
            LOGIN_TEMPLATE, hata="Kullanıcı adı veya şifre hatalı!"
        )

    return render_template_string(LOGIN_TEMPLATE)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    users = kullanicilari_yukle()
    if "user" not in session or session["user"] not in users:
        return redirect(url_for("login"))

    session_user = session["user"]
    is_admin = users[session_user]["rol"] == "admin"

    view_user = request.args.get("view_user")
    if is_admin and view_user in users:
        session["view_user"] = view_user

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    return render_template_string(
        HTML_TEMPLATE,
        veriler=veriler,
        session_user_id=session_user,
        session_user_ad=users[session_user]["ad"],
        aktif_kullanici=target_user,
        aktif_ad=users.get(target_user, {}).get("ad", target_user),
        is_admin=is_admin,
        tum_ogrenciler=users,
    )


@app.route("/uploads/<filename>")
def get_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/upload_new", methods=["POST"])
def upload_new():
    if "user" not in session:
        return jsonify({"success": False})
    file = request.files.get("photo")
    if file:
        filename = f"program_{int(time.time())}.jpg"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)
        veriler["resim"] = filename
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/toggle", methods=["POST"])
def toggle():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun, index = data.get("gun"), data.get("index")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    yeni_durum, tamamlanan, toplam, yuzde = False, 0, 0, 0

    if (
        "program" in veriler
        and gun in veriler["program"]
        and 0 <= index < len(veriler["program"][gun])
    ):
        veriler["program"][gun][index]["tamamlandi"] = not veriler["program"][
            gun
        ][index]["tamamlandi"]
        verileri_kaydet(target_user, veriler)
        yeni_durum = veriler["program"][gun][index]["tamamlandi"]
        etutler = veriler["program"][gun]
        toplam = len(etutler)
        tamamlanan = sum(1 for e in etutler if e.get("tamamlandi"))
        yuzde = int(round((tamamlanan / toplam) * 100)) if toplam > 0 else 0

    return jsonify({
        "success": True,
        "yeni_durum": yeni_durum,
        "tamamlanan": tamamlanan,
        "toplam": toplam,
        "yuzde": yuzde,
    })


@app.route("/edit", methods=["POST"])
def edit():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun, index, baslik, detay = (
        data.get("gun"),
        data.get("index"),
        data.get("baslik"),
        data.get("detay"),
    )

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    if (
        "program" in veriler
        and gun in veriler["program"]
        and 0 <= index < len(veriler["program"][gun])
    ):
        veriler["program"][gun][index]["baslik"] = baslik
        veriler["program"][gun][index]["detay"] = detay
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/toplu_edit", methods=["POST"])
def toplu_edit():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    yeni_program = data.get("program")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    for gun, etutler in yeni_program.items():
        if gun in veriler["program"]:
            for i, yeni_etut in enumerate(etutler):
                if i < len(veriler["program"][gun]):
                    veriler["program"][gun][i]["baslik"] = yeni_etut["baslik"]
                    veriler["program"][gun][i]["detay"] = yeni_etut["detay"]
                else:
                    veriler["program"][gun].append({
                        "baslik": yeni_etut["baslik"],
                        "detay": yeni_etut["detay"],
                        "tamamlandi": False,
                    })

    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/sure_kaydet", methods=["POST"])
def sure_kaydet():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun = data.get("gun")
    sure = data.get("sure")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    if "gunluk_sureler" not in veriler:
        veriler["gunluk_sureler"] = {}

    veriler["gunluk_sureler"][gun] = sure
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/soru_ekle", methods=["POST"])
def soru_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    foto = request.files.get("foto")
    ders = request.form.get("ders", "Diğer")
    not_str = request.form.get("not", "")

    if foto:
        filename = f"soru_{int(time.time())}.jpg"
        foto.save(os.path.join(UPLOAD_FOLDER, filename))

        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)

        yeni_soru = {
            "id": str(int(time.time())),
            "dosya": filename,
            "ders": ders,
            "not": not_str,
        }
        veriler["sorular"].append(yeni_soru)
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/soru_sil", methods=["POST"])
def soru_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    soru_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["sorular"] = [
        s for s in veriler["sorular"] if s.get("id") != soru_id
    ]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/deneme_ekle", methods=["POST"])
def deneme_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    dosya = request.files.get("dosya")
    adi = request.form.get("adi", "Deneme")
    net = request.form.get("net", "")

    filename = ""
    is_image = False
    orj_isim = ""

    if dosya:
        orj_isim = dosya.filename
        ext = os.path.splitext(orj_isim)[1].lower()
        filename = f"deneme_{int(time.time())}{ext}"
        dosya.save(os.path.join(UPLOAD_FOLDER, filename))
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            is_image = True

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    tarih_str = time.strftime("%d.%m.%Y %H:%M")

    yeni_deneme = {
        "id": str(int(time.time())),
        "adi": adi,
        "net": net,
        "dosya": filename,
        "is_image": is_image,
        "orj_isim": orj_isim,
        "tarih": tarih_str,
    }
    veriler["denemeler"].append(yeni_deneme)
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/deneme_sil", methods=["POST"])
def deneme_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    deneme_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["denemeler"] = [
        d for d in veriler["denemeler"] if d.get("id") != deneme_id
    ]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/not_ekle", methods=["POST"])
def not_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    baslik = data.get("baslik")
    icerik = data.get("icerik")

    if baslik and icerik:
        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)
        tarih_str = time.strftime("%d.%m.%Y %H:%M")
        yeni_not = {
            "id": str(int(time.time())),
            "baslik": baslik,
            "icerik": icerik,
            "tarih": tarih_str,
        }
        veriler["notlar"].append(yeni_not)
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/not_sil", methods=["POST"])
def not_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    not_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["notlar"] = [n for n in veriler["notlar"] if n.get("id") != not_id]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


# Admin Kullanıcı Yönetimi Route'ları
@app.route("/kullanici_ekle", methods=["POST"])
def kullanici_ekle():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False, "message": "Yetkiniz yok!"})

    data = request.json
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    fullname = data.get("fullname", "").strip()
    role = data.get("role", "ogrenci")

    if not username or not password or not fullname:
        return jsonify({"success": False, "message": "Eksik bilgi!"})

    if username in users:
        return jsonify(
            {"success": False, "message": "Bu kullanıcı adı zaten mevcut!"}
        )

    users[username] = {"sifre": password, "rol": role, "ad": fullname}
    kullanicilari_kaydet(users)
    return jsonify({"success": True})


@app.route("/sifre_guncelle", methods=["POST"])
def sifre_guncelle():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False})

    data = request.json
    username = data.get("username")
    new_password = data.get("new_password", "").strip()

    if username in users and new_password:
        users[username]["sifre"] = new_password
        kullanicilari_kaydet(users)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/kullanici_sil", methods=["POST"])
def kullanici_sil():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False, "message": "Yetkiniz yok!"})

    data = request.json
    username = data.get("username")

    if username in users and username != "admin" and username != session["user"]:
        del users[username]
        kullanicilari_kaydet(users)

        # Kullanıcının veri dosyasını sil
        filepath = kullanici_dosya_yolu(username)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Bu kullanıcı silinemez!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
import copy
import json
import os
import time
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    send_from_directory,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "mustafa_berk_gizli_anahtar_123"

UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "user_data"
USERS_FILE = "users.json"

for folder in [UPLOAD_FOLDER, DATA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Varsayılan Kullanıcı Kadrosu
VARSAYILAN_USERS = {
    "admin": {"sifre": "admin123", "rol": "admin", "ad": "Yönetici / Koç"},
    "mustafa": {"sifre": "1234", "rol": "ogrenci", "ad": "Mustafa Berk"},
    "ahmet": {"sifre": "1234", "rol": "ogrenci", "ad": "Ahmet Yılmaz"},
    "ayse": {"sifre": "1234", "rol": "ogrenci", "ad": "Ayşe Kaya"},
}


def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(VARSAYILAN_USERS, f, ensure_ascii=False, indent=2)
    return VARSAYILAN_USERS


def kullanicilari_kaydet(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)


VARSAYILAN_PROGRAM = {
    "Pazartesi": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:272-275 | Prf S:153-154",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj tyt S:160-165",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: elektrostatik",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:148-156",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: plm S:179-188",
            "tamamlandi": False,
        },
        {"baslik": "5. Etüt Türkçe", "detay": "Konu: S:", "tamamlandi": False},
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: S:",
            "tamamlandi": False,
        },
        {"baslik": "Geometri", "detay": "Konu: S:", "tamamlandi": False},
        {"baslik": "Sosyal", "detay": "Konu: S:", "tamamlandi": False},
    ],
    "Salı": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:247-250 | Prf S:155-156",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:8-13",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:162-169",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:157-162 + Mol konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: plm S:189-190 | Prf S:157-164",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: 345 S:210-214",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:63-68",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:67-72",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Çarşamba": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:252-255 | Prf S:157-158",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:14-19",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:170-179",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: Aydın fasikül S:26-45 + Mol konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:165-174",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:224-231",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:69-74",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:73-78",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Perşembe": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:256-259 | Prf S:159-160",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj Ayt S:20-23 + tara",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:180-183 | bil.sar S:147-150",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: Aydın fasikül S:46-50 | Plm S:164-169",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:175-184",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:232-237",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:75-80",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: Açıortay S:kenarortay konu",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: bil.sar S:4 test",
            "tamamlandi": False,
        },
    ],
    "Cuma": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:260-263 | Prf S:161-162",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:87-94",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: bil.sar tyt S:151-160",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm S:170-179",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:185-190 + tara",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: bil.sar S:deneme 8 (5-6)",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: 3d tyt S:81-86",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:79-84",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:4. video",
            "tamamlandi": False,
        },
    ],
    "Cumartesi": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:264-267 | Prf S:163-164",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:95-102",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: elk akım S:konu",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: kimyasal tepkimeler ve hesaplamalar konu",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: prf tyt S:193-198 + tara Kalıtım konu",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Konu: limit S:238-243",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: rasyonel tyt S:deneme 2",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:85-90",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:6. video",
            "tamamlandi": False,
        },
    ],
    "Pazar": [
        {
            "baslik": "Paragraf / Problem",
            "detay": "345 S:268-271 | Prf S:165-166",
            "tamamlandi": False,
        },
        {
            "baslik": "1. Etüt Matematik",
            "detay": "Konu: orj fas S:103-110",
            "tamamlandi": False,
        },
        {
            "baslik": "2. Etüt Fizik",
            "detay": "Konu: 345 tyt S:184-191",
            "tamamlandi": False,
        },
        {
            "baslik": "3. Etüt Kimya",
            "detay": "Konu: plm tyt S:59-89 testler",
            "tamamlandi": False,
        },
        {
            "baslik": "4. Etüt Biyoloji",
            "detay": "Konu: kalıtım S:konu",
            "tamamlandi": False,
        },
        {
            "baslik": "5. Etüt Türkçe",
            "detay": "Matris tyt (T: M: F: S: Toplam:)",
            "tamamlandi": False,
        },
        {
            "baslik": "6. Etüt Matematik",
            "detay": "Konu: S:",
            "tamamlandi": False,
        },
        {
            "baslik": "Geometri",
            "detay": "Konu: bil.sar geo S:91-96",
            "tamamlandi": False,
        },
        {
            "baslik": "Sosyal",
            "detay": "Konu: 39 günde S:7. video",
            "tamamlandi": False,
        },
    ],
}


def kullanici_dosya_yolu(username):
    return os.path.join(DATA_FOLDER, f"data_{username}.json")


def verileri_oku(username):
    filepath = kullanici_dosya_yolu(username)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("sorular", [])
                data.setdefault("notlar", [])
                data.setdefault("denemeler", [])
                data.setdefault("gunluk_sureler", {})
                # VARSAYILAN_PROGRAM kopyasını atıyoruz
                data.setdefault("program", copy.deepcopy(VARSAYILAN_PROGRAM))
                data.setdefault("resim", "")
                return data
        except Exception:
            pass
    # Yeni kullanıcı oluşturulurken bağımsız derin kopya oluşturuyoruz
    return {
        "resim": "",
        "program": copy.deepcopy(VARSAYILAN_PROGRAM),
        "sorular": [],
        "notlar": [],
        "denemeler": [],
        "gunluk_sureler": {},
    }


def verileri_kaydet(username, data):
    filepath = kullanici_dosya_yolu(username)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_aktif_kullanici():
    users = kullanicilari_yukle()
    if "user" not in session or session["user"] not in users:
        return None
    session_user = session["user"]
    if users[session_user]["rol"] == "admin":
        view_u = request.args.get("view_user") or session.get("view_user")
        if view_u and view_u in users:
            return view_u
        for u, u_data in users.items():
            if u_data.get("rol") == "ogrenci":
                return u
    return session_user


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Çalışma Paneli - Giriş</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
  body { background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .login-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
  .form-control { background-color: #0f172a; border-color: #334155; color: #f8fafc; }
  .form-control:focus { background-color: #0f172a; border-color: #38bdf8; color: #f8fafc; box-shadow: none; }
  .btn-primary { background-color: #0284c7; border-color: #0284c7; font-weight: 700; }
  .btn-primary:hover { background-color: #0369a1; }
</style>
</head>
<body>
<div class="login-card">
  <h4 class="text-center fw-bold text-info mb-4">📚 Çalışma Paneli</h4>
  {% if hata %}
    <div class="alert alert-danger p-2 text-center small mb-3">{{ hata }}</div>
  {% endif %}
  <form method="POST" action="/login">
    <div class="mb-3">
      <label class="form-label small fw-bold text-secondary">Kullanıcı Adı</label>
      <input type="text" name="username" class="form-control" placeholder="Kullanıcı adınızı girin" required>
    </div>
    <div class="mb-4">
      <label class="form-label small fw-bold text-secondary">Şifre</label>
      <input type="password" name="password" class="form-control" placeholder="Şifrenizi girin" required>
    </div>
    <button type="submit" class="btn btn-primary w-100 py-2">Giriş Yap</button>
  </form>
</div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ aktif_ad }} - Çalışma Paneli</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body, body.theme-blue {
  --bg-main: #0f172a;
  --bg-card: #1e293b;
  --bg-inner: #0f172a;
  --border-color: #334155;
  --accent-color: #38bdf8;
  --accent-hover: #0284c7;
  --text-main: #f8fafc;
  --text-sub: #94a3b8;
  --day-btn-bg: linear-gradient(135deg, #1e293b, #0f172a);
}

body.theme-purple {
  --bg-main: #130a2a;
  --bg-card: #211242;
  --bg-inner: #0b051b;
  --border-color: #4c2885;
  --accent-color: #c084fc;
  --accent-hover: #9333ea;
  --text-main: #faf5ff;
  --text-sub: #c084fc;
  --day-btn-bg: linear-gradient(135deg, #211242, #0b051b);
}

body.theme-green {
  --bg-main: #022c22;
  --bg-card: #064e3b;
  --bg-inner: #022c22;
  --border-color: #047857;
  --accent-color: #34d399;
  --accent-hover: #059669;
  --text-main: #ecfdf5;
  --text-sub: #6ee7b7;
  --day-btn-bg: linear-gradient(135deg, #064e3b, #022c22);
}

body.theme-amber {
  --bg-main: #1c100b;
  --bg-card: #2e1a12;
  --bg-inner: #150b07;
  --border-color: #5c3321;
  --accent-color: #fb923c;
  --accent-hover: #ea580c;
  --text-main: #fff7ed;
  --text-sub: #fdba74;
  --day-btn-bg: linear-gradient(135deg, #2e1a12, #150b07);
}

body {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  overflow-x: hidden;
  padding-bottom: 30px;
  transition: all 0.3s ease;
}

.admin-bar {
  background-color: var(--bg-card);
  border-bottom: 2px solid var(--accent-color);
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.nav-container { display: flex; gap: 6px; padding: 10px; background-color: var(--bg-main); position: sticky; top: 0; z-index: 1000; overflow-x: auto; border-bottom: 1px solid var(--border-color); }
.custom-tab-btn { flex: 1; min-width: 80px; background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 4px; text-align: center; color: var(--text-sub); font-weight: 700; font-size: 0.78rem; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; }
.custom-tab-btn.active { background-color: var(--bg-inner); color: var(--accent-color); border-color: var(--accent-color); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); }

.tab-content-container { padding: 0 10px; }
.tab-pane-custom { display: none; }
.tab-pane-custom.active { display: block; }

.card-dark { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
.day-btn { background: var(--day-btn-bg); border: 1px solid var(--border-color); color: var(--text-main); width: 100%; text-align: left; padding: 14px 18px; border-radius: 10px; font-weight: 700; font-size: 1.05rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; margin-bottom: 10px; }
.progress-badge { font-size: 0.85rem; padding: 4px 10px; border-radius: 20px; background-color: var(--bg-inner); color: var(--accent-color); border: 1px solid var(--border-color); font-weight: 700; }
.time-badge { font-size: 0.82rem; padding: 3px 8px; border-radius: 6px; background-color: rgba(56, 189, 248, 0.15); color: var(--accent-color); margin-left: 8px; border: 1px solid var(--border-color); }
.day-content { display: none; padding: 12px; background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; margin-bottom: 15px; }
.etut-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.box { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px; cursor: pointer; position: relative; transition: transform 0.1s ease; }
.box.completed { background-color: #064e3b !important; border-color: #10b981 !important; }
.box-title { font-weight: 700; font-size: 0.88rem; color: var(--text-main); margin-bottom: 4px; }
.box-detay { font-size: 0.75rem; color: var(--text-sub); word-break: break-word; }
.completed .box-title { color: #ffffff !important; }
.completed .box-detay { color: #a7f3d0 !important; }
.edit-btn { position: absolute; top: 6px; right: 6px; font-size: 11px; background: rgba(255, 255, 255, 0.1); border: none; border-radius: 4px; padding: 2px 5px; color: var(--text-sub); }

.timer-box { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; text-align: center; }
.timer-display { font-size: 2.8rem; font-weight: 800; color: var(--accent-color); font-family: monospace; letter-spacing: 2px; background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; padding: 10px; margin-top: 10px; margin-bottom: 15px; }
.form-control, .form-select { background-color: var(--bg-inner); border-color: var(--border-color); color: var(--text-main); }
.form-control:focus, .form-select:focus { background-color: var(--bg-inner); color: var(--text-main); border-color: var(--accent-color); box-shadow: none; }

.palette-container { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; align-items: center; background: var(--bg-card); padding: 10px; border-radius: 12px; border: 1px solid var(--border-color); flex-wrap: wrap; }
.theme-btn { border-radius: 8px; padding: 6px 14px; font-weight: 700; font-size: 0.8rem; border: 1px solid var(--border-color); cursor: pointer; transition: all 0.2s; }
.theme-btn.btn-blue { background-color: #0f172a; color: #38bdf8; border-color: #38bdf8; }
.theme-btn.btn-purple { background-color: #130a2a; color: #c084fc; border-color: #c084fc; }
.theme-btn.btn-green { background-color: #022c22; color: #34d399; border-color: #34d399; }
.theme-btn.btn-amber { background-color: #1c100b; color: #fb923c; border-color: #fb923c; }

.question-card { background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; height: 100%; }
.question-img { width: 100%; height: 180px; object-fit: cover; cursor: pointer; }

.note-card { background-color: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; position: relative; }
.note-title { font-weight: 700; font-size: 1rem; color: var(--accent-color); margin-bottom: 6px; }
.note-content { font-size: 0.88rem; color: var(--text-main); white-space: pre-wrap; word-break: break-word; }
.note-date { font-size: 0.7rem; color: var(--text-sub); margin-top: 10px; }

.table-dark-custom { background-color: var(--bg-inner); color: var(--text-main); border-color: var(--border-color); }
.table-dark-custom th { background-color: var(--bg-card); color: var(--accent-color); border-color: var(--border-color); font-size: 0.85rem; text-align: center; white-space: nowrap; }
.table-dark-custom td { border-color: var(--border-color); vertical-align: middle; padding: 4px; min-width: 140px; }
.table-input { background-color: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-main); font-size: 0.78rem; padding: 6px; border-radius: 6px; width: 100%; min-height: 50px; }
.etut-label { font-weight: 700; color: #f8fafc; font-size: 0.82rem; text-align: center; background-color: var(--bg-card); }
</style>
</head>
<body>

<div class="admin-bar">
  <div>
    <span class="fw-bold text-info">👤 {{ session_user_ad }}</span>
    {% if is_admin %}
      <span class="badge bg-warning text-dark ms-2">YÖNETİCİ MODU</span>
    {% endif %}
  </div>

  {% if is_admin %}
  <div class="d-flex align-items-center gap-2">
    <label class="small text-light fw-bold">Öğrenci Seç:</label>
    <select class="form-select form-select-sm" onchange="ogrenciDegistir(this.value)">
      {% for u_id, u_info in tum_ogrenciler.items() %}
        {% if u_info.rol == 'ogrenci' %}
          <option value="{{ u_id }}" {% if u_id == aktif_kullanici %}selected{% endif %}>{{ u_info.ad }}</option>
        {% endif %}
      {% endfor %}
    </select>
  </div>
  {% endif %}

  <a href="/logout" class="btn btn-sm btn-outline-danger font-bold">Çıkış Yap</a>
</div>

<div class="nav-container">
  <div class="custom-tab-btn active" id="btn-prog" onclick="switchTab(0)">📅 Program</div>
  <div class="custom-tab-btn" id="btn-edit" onclick="switchTab(1)">⚙️ Düzenle</div>
  <div class="custom-tab-btn" id="btn-timer" onclick="switchTab(2)">⏱️ Kronometre</div>
  <div class="custom-tab-btn" id="btn-soru" onclick="switchTab(3)">❓ Sorular</div>
  <div class="custom-tab-btn" id="btn-analiz" onclick="switchTab(4)">📊 Deneme Analizi</div>
  <div class="custom-tab-btn" id="btn-not" onclick="switchTab(5)">📝 Notlarım</div>
  {% if is_admin %}
  <div class="custom-tab-btn" id="btn-users" onclick="switchTab(6)">👥 Kullanıcı Yönetimi</div>
  {% endif %}
</div>

<div class="tab-content-container">

<div class="palette-container">
  <small class="fw-bold text-secondary me-2">🎨 Renk Teması Seç:</small>
  <button class="theme-btn btn-blue" onclick="setTheme('theme-blue')">Gece Mavisi</button>
  <button class="theme-btn btn-purple" onclick="setTheme('theme-purple')">Siber Mor</button>
  <button class="theme-btn btn-green" onclick="setTheme('theme-green')">Zümrüt Yeşil</button>
  <button class="theme-btn btn-amber" onclick="setTheme('theme-amber')">Gün Batımı</button>
</div>

<div class="tab-pane-custom active" id="pane-prog">
  <div class="card card-dark p-3 mb-3">
    <label class="fw-bold mb-2 text-light">📸 Program Fotoğrafı Yükle / Değiştir:</label>
    <div class="input-group">
      <input type="file" id="imageInput" class="form-control" accept="image/*">
      <button class="btn btn-primary fw-bold" onclick="uploadNewProgram()">Yükle</button>
    </div>
  </div>

  {% if veriler.resim %}
  <div class="card card-dark p-2 mb-3 text-center">
    <img src="/uploads/{{ veriler.resim }}" class="img-fluid rounded border border-secondary" style="max-height: 300px; object-fit: contain;">
  </div>
  {% endif %}

  <div class="card card-dark p-3">
    <h6 class="fw-bold text-center mb-3 text-light">✨ {{ aktif_ad }} - Güncel Haftalık Programı</h6>
    {% set gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"] %}
    {% for gun in gunler %}
      {% set etutler = veriler.program[gun] %}
      {% set toplam = etutler | length %}
      {% set tamamlanan = etutler | selectattr("tamamlandi", "equalto", true) | list | length %}
      {% set yuzde = (tamamlanan / toplam * 100) | round | int if toplam > 0 else 0 %}
      {% set gun_suresi = veriler.gunluk_sureler.get(gun, "") %}

      <button class="day-btn" onclick="toggleDay('{{ gun }}')">
        <div>
          <span>{{ gun }}</span>
          {% if gun_suresi %}
            <span class="time-badge">⏱️ {{ gun_suresi }}</span>
          {% endif %}
        </div>
        <span class="progress-badge" id="badge-{{ gun }}">%{{ yuzde }} ({{ tamamlanan }}/{{ toplam }})</span>
      </button>

      <div id="day-{{ gun }}" class="day-content">
        <div class="etut-grid">
        {% for row_idx in range(etutler | length) %}
          {% set etut = etutler[row_idx] %}
          <div class="box {% if etut.tamamlandi %}completed{% endif %}" id="box-{{ gun }}-{{ row_idx }}" onclick="toggleEtut('{{ gun }}', {{ row_idx }})">
            <button class="edit-btn" onclick="editEtut(event, '{{ gun }}', {{ row_idx }}, '{{ etut.baslik }}', '{{ etut.detay }}')">✏️</button>
            <div class="box-title" id="title-{{ gun }}-{{ row_idx }}">{{ etut.baslik }}</div>
            <div class="box-detay" id="detay-{{ gun }}-{{ row_idx }}">{{ etut.detay }}</div>
          </div>
        {% endfor %}
        </div>
      </div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-edit">
  <div class="card card-dark p-3 mb-3">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-bold text-light m-0">⚙️ Kağıt Düzeninde Haftalık Program Tablosu ({{ aktif_ad }})</h6>
      <button class="btn btn-sm btn-success fw-bold" onclick="topluKaydet()">💾 Değişiklikleri Kaydet</button>
    </div>

    {% set etut_listesi = veriler.program["Pazartesi"] %}
    <div class="table-responsive">
      <table class="table table-dark-custom table-bordered align-middle m-0">
        <thead>
          <tr>
            <th style="min-width: 140px;" class="text-center bg-dark text-info">Etüt / Ders</th>
            {% for gun in gunler %}
              <th style="min-width: 150px;">{{ gun }}</th>
            {% endfor %}
          </tr>
        </thead>
        <tbody>
          {% for e_idx in range(etut_listesi | length) %}
            <tr>
              <td class="etut-label">
                <input type="text" class="form-control text-center fw-bold bg-dark text-info border-secondary mb-1" id="etut-baslik-row-{{ e_idx }}" value="{{ etut_listesi[e_idx].baslik }}">
              </td>
              {% for gun in gunler %}
                <td>
                  <textarea class="form-control table-input" id="tablo-detay-{{ gun }}-{{ e_idx }}" rows="2">{{ veriler.program[gun][e_idx].detay if e_idx < (veriler.program[gun] | length) else '' }}</textarea>
                </td>
              {% endfor %}
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    <button class="btn btn-success fw-bold mt-3 w-100 py-2" onclick="topluKaydet()">💾 Tüm Tabloyu Kaydet</button>
  </div>
</div>

<div class="tab-pane-custom" id="pane-timer">
  <div class="timer-box">
    <h5 class="fw-bold text-light mb-2">⏱️ Çalışma Kronometresi</h5>
    <div class="timer-display" id="stopwatchDisplay">00:00:00</div>
    <div class="d-flex justify-content-center gap-2 mb-3">
      <button class="btn btn-success fw-bold px-4" onclick="startStopwatch()">Başlat</button>
      <button class="btn btn-warning fw-bold px-4 text-dark" onclick="pauseStopwatch()">Durdur</button>
      <button class="btn btn-danger fw-bold px-4" onclick="resetStopwatch()">Sıfırla</button>
    </div>

    <div class="row g-2 align-items-center justify-content-center pt-3 border-top border-secondary">
      <div class="col-md-6 col-8">
        <select id="kayitGunSelect" class="form-select text-center fw-bold">
          {% for gun in gunler %}
            <option value="{{ gun }}">{{ gun }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-4 col-4">
        <button class="btn btn-info w-100 fw-bold text-dark" onclick="sureyiGuneKaydet()">📌 Güne Kaydet</button>
      </div>
    </div>
  </div>

  <div class="timer-box">
    <h5 class="fw-bold text-light mb-2">⏳ Deneme Geri Sayımı (Dakika)</h5>
    <div class="input-group mb-3">
      <input type="number" id="countdownInput" class="form-control text-center" placeholder="Örn: 135" value="135">
      <button class="btn btn-info fw-bold text-dark" onclick="startCountdown()">Kur & Başlat</button>
    </div>
    <div class="timer-display" id="countdownDisplay">02:15:00</div>
    <div class="d-flex justify-content-center gap-2">
      <button class="btn btn-secondary fw-bold px-4" onclick="stopCountdown()">İptal Et</button>
    </div>
  </div>
</div>

<div class="tab-pane-custom" id="pane-soru">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📌 Yapılamayan Soru Ekle ({{ aktif_ad }})</h6>
    <div class="row g-2">
      <div class="col-md-4">
        <select id="soruDers" class="form-select">
          <option value="Matematik">Matematik</option>
          <option value="Fizik">Fizik</option>
          <option value="Kimya">Kimya</option>
          <option value="Biyoloji">Biyoloji</option>
          <option value="Geometri">Geometri</option>
          <option value="Türkçe">Türkçe</option>
          <option value="Sosyal">Sosyal</option>
        </select>
      </div>
      <div class="col-md-8">
        <input type="text" id="soruNot" class="form-control" placeholder="Not/Sayfa/Soru No (Opsiyonel)">
      </div>
      <div class="col-12 mt-2">
        <input type="file" id="soruFoto" class="form-control" accept="image/*">
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="soruEkle()">Soru Kaydet</button>
      </div>
    </div>
  </div>

  <div class="row g-3">
    {% for soru in veriler.sorular %}
    <div class="col-6 col-md-4" id="soru-card-{{ soru.id }}">
      <div class="question-card p-2 text-center">
        <a href="/uploads/{{ soru.dosya }}" target="_blank">
          <img src="/uploads/{{ soru.dosya }}" class="question-img rounded mb-2">
        </a>
        <span class="badge bg-primary mb-1">{{ soru.ders }}</span>
        <div class="small text-secondary mb-2">{{ soru.not }}</div>
        <button class="btn btn-sm btn-outline-danger w-100" onclick="soruSil('{{ soru.id }}')">Çözüldü / Sil</button>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş yapılmayan soru yok! 🎉</div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-analiz">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📈 Yeni Deneme / Analiz Dosyası Ekle ({{ aktif_ad }})</h6>
    <div class="row g-2">
      <div class="col-md-6">
        <input type="text" id="denemeAdi" class="form-control" placeholder="Deneme Adı (Örn: 3D TYT Deneme 1)">
      </div>
      <div class="col-md-6">
        <input type="text" id="denemeNet" class="form-control" placeholder="Net Bilgisi / Not (Örn: TYT 85.5 Net)">
      </div>
      <div class="col-12 mt-2">
        <label class="text-secondary small mb-1">Fotoğraf veya Belge Seç (PDF, Word, Görsel vs.):</label>
        <input type="file" id="denemeDosya" class="form-control">
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="denemeEkle()">Analizi Kaydet</button>
      </div>
    </div>
  </div>

  <div class="row g-3">
    {% for deneme in veriler.denemeler %}
    <div class="col-12 col-md-6" id="deneme-card-{{ deneme.id }}">
      <div class="note-card">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div class="note-title">{{ deneme.adi }}</div>
          <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="denemeSil('{{ deneme.id }}')">🗑️ Sil</button>
        </div>
        <div class="fw-bold text-light mb-2">🎯 {{ deneme.net }}</div>
        {% if deneme.is_image %}
          <a href="/uploads/{{ deneme.dosya }}" target="_blank">
            <img src="/uploads/{{ deneme.dosya }}" class="img-fluid rounded mb-2 border border-secondary" style="max-height: 200px; width: 100%; object-fit: cover;">
          </a>
        {% else %}
          <div class="p-2 mb-2 bg-dark rounded border border-secondary text-center">
            <a href="/uploads/{{ deneme.dosya }}" target="_blank" class="btn btn-sm btn-outline-info text-decoration-none fw-bold">
              📄 Dosyayı / Analizi Aç ({{ deneme.orj_isim }})
            </a>
          </div>
        {% endif %}
        <div class="note-date">📅 Eklenme Tarihi: {{ deneme.tarih }}</div>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş deneme analizi yok! 📈</div>
    {% endfor %}
  </div>
</div>

<div class="tab-pane-custom" id="pane-not">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-light mb-3">📝 Yeni Not Ekle ({{ aktif_ad }})</h6>
    <input type="text" id="notBaslik" class="form-control mb-2" placeholder="Not Başlığı (Örn: Formüller / Hatırlatma)">
    <textarea id="notIcerik" class="form-control mb-3" rows="3" placeholder="Notunu buraya yaz..."></textarea>
    <button class="btn btn-success w-100 fw-bold" onclick="notEkle()">Notu Kaydet</button>
  </div>

  <div class="row g-3">
    {% for not_item in veriler.notlar %}
    <div class="col-12 col-md-6" id="note-card-{{ not_item.id }}">
      <div class="note-card">
        <div class="d-flex justify-content-between align-items-start">
          <div class="note-title">{{ not_item.baslik }}</div>
          <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="notSil('{{ not_item.id }}')">🗑️ Sil</button>
        </div>
        <div class="note-content">{{ not_item.icerik }}</div>
        <div class="note-date">📅 {{ not_item.tarih }}</div>
      </div>
    </div>
    {% else %}
    <div class="text-center text-muted my-4">Henüz kaydedilmiş bir notun yok! ✍️</div>
    {% endfor %}
  </div>
</div>

{% if is_admin %}
<div class="tab-pane-custom" id="pane-users">
  <div class="card card-dark p-3 mb-3">
    <h6 class="fw-bold text-info mb-3">➕ Yeni Öğrenci / Kullanıcı Ekle</h6>
    <div class="row g-2">
      <div class="col-md-3">
        <input type="text" id="kullaniciKullaniciAdi" class="form-control" placeholder="Kullanıcı Adı (Örn: mehmet)">
      </div>
      <div class="col-md-3">
        <input type="text" id="kullaniciSifre" class="form-control" placeholder="Şifre (Örn: 1234)">
      </div>
      <div class="col-md-4">
        <input type="text" id="kullaniciAdSoyad" class="form-control" placeholder="Ad Soyad (Örn: Mehmet Öz)">
      </div>
      <div class="col-md-2">
        <select id="kullaniciRol" class="form-select">
          <option value="ogrenci">Öğrenci</option>
          <option value="admin">Yönetici</option>
        </select>
      </div>
      <div class="col-12 mt-2">
        <button class="btn btn-success w-100 fw-bold" onclick="kullaniciEkle()">Kullanıcıyı Kaydet</button>
      </div>
    </div>
  </div>

  <div class="card card-dark p-3">
    <h6 class="fw-bold text-light mb-3">👥 Mevcut Kullanıcılar ve Şifre Düzenleme</h6>
    <div class="table-responsive">
      <table class="table table-dark-custom align-middle m-0">
        <thead>
          <tr>
            <th>Kullanıcı Adı</th>
            <th>Ad Soyad</th>
            <th>Rol</th>
            <th>Şifre Değiştir</th>
            <th>İşlem</th>
          </tr>
        </thead>
        <tbody>
          {% for u_id, u_info in tum_ogrenciler.items() %}
          <tr>
            <td class="fw-bold text-info">{{ u_id }}</td>
            <td>{{ u_info.ad }}</td>
            <td>
              <span class="badge {% if u_info.rol == 'admin' %}bg-warning text-dark{% else %}bg-primary{% endif %}">
                {{ u_info.rol }}
              </span>
            </td>
            <td>
              <div class="input-group input-group-sm">
                <input type="text" id="sifre-input-{{ u_id }}" class="form-control" value="{{ u_info.sifre }}">
                <button class="btn btn-outline-info" onclick="sifreGuncelle('{{ u_id }}')">Güncelle</button>
              </div>
            </td>
            <td>
              {% if u_id != 'admin' and u_id != session_user_id %}
                <button class="btn btn-sm btn-outline-danger" onclick="kullaniciSil('{{ u_id }}')">🗑️ Sil</button>
              {% else %}
                <span class="text-secondary small">Korumalı</span>
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endif %}

</div>

<script>
function ogrenciDegistir(username) {
  window.location.href = "/?view_user=" + username;
}

function setTheme(themeName) {
  document.body.className = '';
  document.body.classList.add(themeName);
  localStorage.setItem('selectedTheme', themeName);
}

(function loadSavedTheme() {
  let savedTheme = localStorage.getItem('selectedTheme') || 'theme-blue';
  document.body.classList.add(savedTheme);
})();

function switchTab(index) {
  const tabs = ['pane-prog', 'pane-edit', 'pane-timer', 'pane-soru', 'pane-analiz', 'pane-not', 'pane-users'];
  const btns = ['btn-prog', 'btn-edit', 'btn-timer', 'btn-soru', 'btn-analiz', 'btn-not', 'btn-users'];
  tabs.forEach((tab, i) => {
    let tabEl = document.getElementById(tab);
    let btnEl = document.getElementById(btns[i]);
    if (tabEl) tabEl.classList.toggle('active', i === index);
    if (btnEl) btnEl.classList.toggle('active', i === index);
  });
}

function toggleDay(gun) {
  let el = document.getElementById('day-' + gun);
  el.style.display = (el.style.display === "block") ? "none" : "block";
}

async function uploadNewProgram() {
  let input = document.getElementById('imageInput');
  if (input.files.length === 0) return alert("Lütfen bir resim dosyası seçin!");
  let formData = new FormData();
  formData.append('photo', input.files[0]);
  let res = await fetch('/upload_new', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function toggleEtut(gun, index) {
  let res = await fetch('/toggle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, index: index})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`box-${gun}-${index}`).classList.toggle('completed', data.yeni_durum);
    document.getElementById(`badge-${gun}`).innerText = `%${data.yuzde} (${data.tamamlanan}/${data.toplam})`;
  }
}

async function editEtut(event, gun, index, mevBaslik, mevDetay) {
  event.stopPropagation();
  let yBaslik = prompt("Ders/Etüt Adı:", mevBaslik);
  if (yBaslik === null) return;
  let yDetay = prompt("Sayfa / Soru Detayı:", mevDetay);
  if (yDetay === null) return;

  let res = await fetch('/edit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, index: index, baslik: yBaslik, detay: yDetay})
  });
  let data = await res.json();
  if (data.success) location.reload();
}

async function topluKaydet() {
  let yeniProgram = {};
  const gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];

  gunler.forEach(gun => {
    yeniProgram[gun] = [];
  });

  let eIdx = 0;
  while (true) {
    let baslikEl = document.getElementById(`etut-baslik-row-${eIdx}`);
    if (!baslikEl) break;
    let baslikVal = baslikEl.value;

    gunler.forEach(gun => {
      let detayEl = document.getElementById(`tablo-detay-${gun}-${eIdx}`);
      let detayVal = detayEl ? detayEl.value : "";
      yeniProgram[gun].push({
        baslik: baslikVal,
        detay: detayVal
      });
    });
    eIdx++;
  }

  let res = await fetch('/toplu_edit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({program: yeniProgram})
  });
  let data = await res.json();
  if (data.success) {
    alert("Program başarıyla güncellendi!");
    location.reload();
  }
}

async function sureyiGuneKaydet() {
  let gun = document.getElementById('kayitGunSelect').value;
  let sure = document.getElementById('stopwatchDisplay').innerText;

  if (sure === "00:00:00") {
    return alert("Henüz bir süre kaydetmediniz!");
  }

  let res = await fetch('/sure_kaydet', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({gun: gun, sure: sure})
  });
  let data = await res.json();
  if (data.success) {
    alert(`${gun} günü için çalışma süresi (${sure}) kaydedildi!`);
    location.reload();
  }
}

async function soruEkle() {
  let foto = document.getElementById('soruFoto').files[0];
  let ders = document.getElementById('soruDers').value;
  let not = document.getElementById('soruNot').value;

  if (!foto) return alert("Lütfen sorunun fotoğrafını seçin!");

  let formData = new FormData();
  formData.append('foto', foto);
  formData.append('ders', ders);
  formData.append('not', not);

  let res = await fetch('/soru_ekle', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function soruSil(soruId) {
  if (!confirm("Bu soruyu silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/soru_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: soruId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`soru-card-${soruId}`).remove();
  }
}

async function denemeEkle() {
  let adi = document.getElementById('denemeAdi').value.trim();
  let net = document.getElementById('denemeNet').value.trim();
  let dosya = document.getElementById('denemeDosya').files[0];

  if (!adi) return alert("Lütfen deneme adını girin!");

  let formData = new FormData();
  formData.append('adi', adi);
  formData.append('net', net);
  if (dosya) formData.append('dosya', dosya);

  let res = await fetch('/deneme_ekle', { method: 'POST', body: formData });
  let data = await res.json();
  if (data.success) location.reload();
}

async function denemeSil(denemeId) {
  if (!confirm("Bu deneme analizini silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/deneme_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: denemeId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`deneme-card-${denemeId}`).remove();
  }
}

async function notEkle() {
  let baslik = document.getElementById('notBaslik').value.trim();
  let icerik = document.getElementById('notIcerik').value.trim();

  if (!baslik || !icerik) return alert("Lütfen hem başlığı hem de not içeriğini girin!");

  let res = await fetch('/not_ekle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({baslik: baslik, icerik: icerik})
  });
  let data = await res.json();
  if (data.success) location.reload();
}

async function notSil(notId) {
  if (!confirm("Bu notu silmek istediğinize emin misiniz?")) return;
  let res = await fetch('/not_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: notId})
  });
  let data = await res.json();
  if (data.success) {
    document.getElementById(`note-card-${notId}`).remove();
  }
}

async function kullaniciEkle() {
  let username = document.getElementById('kullaniciKullaniciAdi').value.trim();
  let password = document.getElementById('kullaniciSifre').value.trim();
  let fullname = document.getElementById('kullaniciAdSoyad').value.trim();
  let role = document.getElementById('kullaniciRol').value;

  if (!username || !password || !fullname) return alert("Lütfen tüm alanları doldurun!");

  let res = await fetch('/kullanici_ekle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: username, password: password, fullname: fullname, role: role})
  });
  let data = await res.json();
  if (data.success) {
    alert("Kullanıcı başarıyla eklendi!");
    location.reload();
  } else {
    alert(data.message || "Hata oluştu!");
  }
}

async function sifreGuncelle(targetUsername) {
  let newPassword = document.getElementById(`sifre-input-${targetUsername}`).value.trim();
  if (!newPassword) return alert("Şifre boş olamaz!");

  let res = await fetch('/sifre_guncelle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: targetUsername, new_password: newPassword})
  });
  let data = await res.json();
  if (data.success) {
    alert(`${targetUsername} kullanıcısının şifresi güncellendi!`);
  } else {
    alert("Şifre güncellenemedi!");
  }
}

async function kullaniciSil(targetUsername) {
  if (!confirm(`${targetUsername} kullanıcısını ve verilerini silmek istediğinize emin misiniz?`)) return;

  let res = await fetch('/kullanici_sil', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: targetUsername})
  });
  let data = await res.json();
  if (data.success) {
    alert("Kullanıcı silindi!");
    location.reload();
  } else {
    alert(data.message || "Silme işlemi başarısız!");
  }
}

let swSeconds = 0, swInterval = null;
function startStopwatch() {
  if (swInterval) return;
  swInterval = setInterval(() => {
    swSeconds++;
    let hrs = Math.floor(swSeconds / 3600).toString().padStart(2, '0');
    let mins = Math.floor((swSeconds % 3600) / 60).toString().padStart(2, '0');
    let secs = (swSeconds % 60).toString().padStart(2, '0');
    document.getElementById('stopwatchDisplay').innerText = `${hrs}:${mins}:${secs}`;
  }, 1000);
}
function pauseStopwatch() { clearInterval(swInterval); swInterval = null; }
function resetStopwatch() { pauseStopwatch(); swSeconds = 0; document.getElementById('stopwatchDisplay').innerText = "00:00:00"; }

let cdSeconds = 135 * 60, cdInterval = null;
function startCountdown() {
  stopCountdown();
  let minsVal = parseInt(document.getElementById('countdownInput').value);
  if (isNaN(minsVal) || minsVal <= 0) return alert("Geçerli bir dakika gir!");
  cdSeconds = minsVal * 60;

  cdInterval = setInterval(() => {
    if (cdSeconds <= 0) {
      clearInterval(cdInterval);
      alert("Süre bitti!");
      return;
    }
    cdSeconds--;
    let hrs = Math.floor(cdSeconds / 3600).toString().padStart(2, '0');
    let mins = Math.floor((cdSeconds % 3600) / 60).toString().padStart(2, '0');
    let secs = (cdSeconds % 60).toString().padStart(2, '0');
    document.getElementById('countdownDisplay').innerText = `${hrs}:${mins}:${secs}`;
  }, 1000);
}
function stopCountdown() { clearInterval(cdInterval); cdInterval = null; }
</script>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    users = kullanicilari_yukle()
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if username in users and users[username]["sifre"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        return render_template_string(
            LOGIN_TEMPLATE, hata="Kullanıcı adı veya şifre hatalı!"
        )

    return render_template_string(LOGIN_TEMPLATE)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    users = kullanicilari_yukle()
    if "user" not in session or session["user"] not in users:
        return redirect(url_for("login"))

    session_user = session["user"]
    is_admin = users[session_user]["rol"] == "admin"

    view_user = request.args.get("view_user")
    if is_admin and view_user in users:
        session["view_user"] = view_user

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    return render_template_string(
        HTML_TEMPLATE,
        veriler=veriler,
        session_user_id=session_user,
        session_user_ad=users[session_user]["ad"],
        aktif_kullanici=target_user,
        aktif_ad=users.get(target_user, {}).get("ad", target_user),
        is_admin=is_admin,
        tum_ogrenciler=users,
    )


@app.route("/uploads/<filename>")
def get_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/upload_new", methods=["POST"])
def upload_new():
    if "user" not in session:
        return jsonify({"success": False})
    file = request.files.get("photo")
    if file:
        filename = f"program_{int(time.time())}.jpg"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)
        veriler["resim"] = filename
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/toggle", methods=["POST"])
def toggle():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun, index = data.get("gun"), data.get("index")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    yeni_durum, tamamlanan, toplam, yuzde = False, 0, 0, 0

    if (
        "program" in veriler
        and gun in veriler["program"]
        and 0 <= index < len(veriler["program"][gun])
    ):
        veriler["program"][gun][index]["tamamlandi"] = not veriler["program"][
            gun
        ][index]["tamamlandi"]
        verileri_kaydet(target_user, veriler)
        yeni_durum = veriler["program"][gun][index]["tamamlandi"]
        etutler = veriler["program"][gun]
        toplam = len(etutler)
        tamamlanan = sum(1 for e in etutler if e.get("tamamlandi"))
        yuzde = int(round((tamamlanan / toplam) * 100)) if toplam > 0 else 0

    return jsonify({
        "success": True,
        "yeni_durum": yeni_durum,
        "tamamlanan": tamamlanan,
        "toplam": toplam,
        "yuzde": yuzde,
    })


@app.route("/edit", methods=["POST"])
def edit():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun, index, baslik, detay = (
        data.get("gun"),
        data.get("index"),
        data.get("baslik"),
        data.get("detay"),
    )

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    if (
        "program" in veriler
        and gun in veriler["program"]
        and 0 <= index < len(veriler["program"][gun])
    ):
        veriler["program"][gun][index]["baslik"] = baslik
        veriler["program"][gun][index]["detay"] = detay
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/toplu_edit", methods=["POST"])
def toplu_edit():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    yeni_program = data.get("program")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    for gun, etutler in yeni_program.items():
        if gun in veriler["program"]:
            for i, yeni_etut in enumerate(etutler):
                if i < len(veriler["program"][gun]):
                    veriler["program"][gun][i]["baslik"] = yeni_etut["baslik"]
                    veriler["program"][gun][i]["detay"] = yeni_etut["detay"]
                else:
                    veriler["program"][gun].append({
                        "baslik": yeni_etut["baslik"],
                        "detay": yeni_etut["detay"],
                        "tamamlandi": False,
                    })

    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/sure_kaydet", methods=["POST"])
def sure_kaydet():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    gun = data.get("gun")
    sure = data.get("sure")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    if "gunluk_sureler" not in veriler:
        veriler["gunluk_sureler"] = {}

    veriler["gunluk_sureler"][gun] = sure
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/soru_ekle", methods=["POST"])
def soru_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    foto = request.files.get("foto")
    ders = request.form.get("ders", "Diğer")
    not_str = request.form.get("not", "")

    if foto:
        filename = f"soru_{int(time.time())}.jpg"
        foto.save(os.path.join(UPLOAD_FOLDER, filename))

        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)

        yeni_soru = {
            "id": str(int(time.time())),
            "dosya": filename,
            "ders": ders,
            "not": not_str,
        }
        veriler["sorular"].append(yeni_soru)
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/soru_sil", methods=["POST"])
def soru_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    soru_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["sorular"] = [
        s for s in veriler["sorular"] if s.get("id") != soru_id
    ]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/deneme_ekle", methods=["POST"])
def deneme_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    dosya = request.files.get("dosya")
    adi = request.form.get("adi", "Deneme")
    net = request.form.get("net", "")

    filename = ""
    is_image = False
    orj_isim = ""

    if dosya:
        orj_isim = dosya.filename
        ext = os.path.splitext(orj_isim)[1].lower()
        filename = f"deneme_{int(time.time())}{ext}"
        dosya.save(os.path.join(UPLOAD_FOLDER, filename))
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            is_image = True

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)
    tarih_str = time.strftime("%d.%m.%Y %H:%M")

    yeni_deneme = {
        "id": str(int(time.time())),
        "adi": adi,
        "net": net,
        "dosya": filename,
        "is_image": is_image,
        "orj_isim": orj_isim,
        "tarih": tarih_str,
    }
    veriler["denemeler"].append(yeni_deneme)
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/deneme_sil", methods=["POST"])
def deneme_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    deneme_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["denemeler"] = [
        d for d in veriler["denemeler"] if d.get("id") != deneme_id
    ]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


@app.route("/not_ekle", methods=["POST"])
def not_ekle():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    baslik = data.get("baslik")
    icerik = data.get("icerik")

    if baslik and icerik:
        target_user = get_aktif_kullanici()
        veriler = verileri_oku(target_user)
        tarih_str = time.strftime("%d.%m.%Y %H:%M")
        yeni_not = {
            "id": str(int(time.time())),
            "baslik": baslik,
            "icerik": icerik,
            "tarih": tarih_str,
        }
        veriler["notlar"].append(yeni_not)
        verileri_kaydet(target_user, veriler)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/not_sil", methods=["POST"])
def not_sil():
    if "user" not in session:
        return jsonify({"success": False})
    data = request.json
    not_id = data.get("id")

    target_user = get_aktif_kullanici()
    veriler = verileri_oku(target_user)

    veriler["notlar"] = [n for n in veriler["notlar"] if n.get("id") != not_id]
    verileri_kaydet(target_user, veriler)
    return jsonify({"success": True})


# Admin Kullanıcı Yönetimi Route'ları
@app.route("/kullanici_ekle", methods=["POST"])
def kullanici_ekle():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False, "message": "Yetkiniz yok!"})

    data = request.json
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    fullname = data.get("fullname", "").strip()
    role = data.get("role", "ogrenci")

    if not username or not password or not fullname:
        return jsonify({"success": False, "message": "Eksik bilgi!"})

    if username in users:
        return jsonify(
            {"success": False, "message": "Bu kullanıcı adı zaten mevcut!"}
        )

    users[username] = {"sifre": password, "rol": role, "ad": fullname}
    kullanicilari_kaydet(users)
    return jsonify({"success": True})


@app.route("/sifre_guncelle", methods=["POST"])
def sifre_guncelle():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False})

    data = request.json
    username = data.get("username")
    new_password = data.get("new_password", "").strip()

    if username in users and new_password:
        users[username]["sifre"] = new_password
        kullanicilari_kaydet(users)
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/kullanici_sil", methods=["POST"])
def kullanici_sil():
    users = kullanicilari_yukle()
    if (
        "user" not in session
        or users.get(session["user"], {}).get("rol") != "admin"
    ):
        return jsonify({"success": False, "message": "Yetkiniz yok!"})

    data = request.json
    username = data.get("username")

    if username in users and username != "admin" and username != session["user"]:
        del users[username]
        kullanicilari_kaydet(users)

        # Kullanıcının veri dosyasını sil
        filepath = kullanici_dosya_yolu(username)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Bu kullanıcı silinemez!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
