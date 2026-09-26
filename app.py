from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Örnek basit Flask uygulaması
@app.route('/')
def home():
    return "<h1>Ders Takip Sistemi Çalışıyor!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
