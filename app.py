from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Örnek ders verileri
courses = [
    {"id": 1, "name": "Matematik", "teacher": "Ahmet Hoca", "credit": 4},
    {"id": 2, "name": "Fizik", "teacher": "Ayşe Hoca", "credit": 3},
    {"id": 3, "name": "Kimya", "teacher": "Mehmet Hoca", "credit": 3}
]

course_stats = {
    "Matematik": {"total": 20, "attended": 18},
    "Fizik": {"total": 15, "attended": 12},
    "Kimya": {"total": 12, "attended": 10}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ders Takip Sistemi</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f4f9; color: #333; }
        h1 { color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>📚 Ders Takip Sistemi</h1>
    
    <div class="card">
        <h2>Ders Listesi</h2>
        <table>
            <tr>
                <th>Ders Adı</th>
                <th>Öğretmen</th>
                <th>Kredi</th>
            </tr>
            {% for course in courses %}
            <tr>
                <td>{{ course.name }}</td>
                <td>{{ course.teacher }}</td>
                <td>{{ course.credit }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h2>Devam Durumu</h2>
        <table>
            <tr>
                <th>Ders</th>
                <th>Toplam Ders</th>
                <th>Katıldığı</th>
                <th>Devam Oranı</th>
            </tr>
            {% for course, stat in course_stats.items() %}
            <tr>
                <td>{{ course }}</td>
                <td>{{ stat.total }}</td>
                <td>{{ stat.attended }}</td>
                <td>%{{ (stat.attended / stat.total * 100) | round(1) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, courses=courses, course_stats=course_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
