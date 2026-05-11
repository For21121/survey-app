import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key-12345')

# ===== НАСТРОЙКИ =====
SURVEY_CODE = "opros-2024"
ADMIN_PASSWORD = "admin-2024"

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'responses.json')

QUESTIONS = [
    {"id": 1, "text": "Курите ли вы или хотите попробовать?", "type": "radio", "options": ["Да", "Нет", "Хочу попробовать"]},
    {"id": 2, "text": "Если да, что вы курите?", "type": "radio", "options": ["Сигареты", "Электронные сигареты", "Оба варианта", "Не курю"]},
    {"id": 3, "text": "Как часто вы курите?", "type": "radio", "options": ["Не каждый день", "1-5 раз в день", "5-8 раз в день", "8-15 раз в день", "Более 15 раз в день", "Не курю"]},
    {"id": 4, "text": "Как долго вы курите? (в годах или месяцах)", "type": "text", "placeholder": "Например: 2 года, 6 месяцев..."},
    {"id": 5, "text": "В каких ситуациях вы курите?", "type": "checkbox", "options": ["Только когда захочется", "Только за компанию", "Только во время стресса (чтобы успокоиться)", "Другое"]},
    {"id": 6, "text": "Сколько приблизительно денежных средств вы тратите на электронные сигареты в месяц?", "type": "radio", "options": ["До 300₽", "До 500₽", "До 800₽", "До 1200₽", "Более 1200₽", "Не трачу"]},
    {"id": 7, "text": "Чем, по вашему, отличаются электронные сигареты от обычных?", "type": "textarea", "placeholder": "Ваш ответ... (если не знаете, предположите)"},
    {"id": 8, "text": "Планируете ли вы в дальнейшем бросить курить?", "type": "radio", "options": ["Да", "Нет", "Не знаю"]},
    {"id": 9, "text": "Ваш пол", "type": "radio", "options": ["Мужской", "Женский"]},
    {"id": 10, "text": "Ваш возраст", "type": "number", "placeholder": "Введите ваш возраст"}
]

def load_responses():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_responses(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_stats(responses):
    if not responses:
        return {}
    stats = {}
    total = len(responses)
    for q in QUESTIONS:
        q_id = str(q["id"])
        q_stats = {"total": total, "question": q["text"], "type": q["type"]}
        if q["type"] in ["radio", "checkbox"]:
            counts = {}
            for resp in responses:
                ans = resp.get(q_id, "")
                if q["type"] == "checkbox":
                    if isinstance(ans, list):
                        for opt in ans: counts[opt] = counts.get(opt, 0) + 1
                    elif ans: counts[ans] = counts.get(ans, 0) + 1
                else:
                    counts[ans] = counts.get(ans, 0) + 1
            percentages = {opt: {"count": cnt, "percent": round((cnt/total)*100, 1)} for opt, cnt in counts.items()}
            q_stats["counts"] = counts
            q_stats["percentages"] = percentages
            q_stats["options"] = q.get("options", [])
        elif q["type"] == "number":
            ages = [int(resp.get(q_id, 0)) for resp in responses if str(resp.get(q_id, "")).isdigit()]
            if ages:
                q_stats["average"] = round(sum(ages)/len(ages), 1)
                q_stats["min"] = min(ages)
                q_stats["max"] = max(ages)
                groups = {"До 18": 0, "18-25": 0, "26-35": 0, "36-50": 0, "50+": 0}
                for age in ages:
                    if age < 18: groups["До 18"] += 1
                    elif age <= 25: groups["18-25"] += 1
                    elif age <= 35: groups["26-35"] += 1
                    elif age <= 50: groups["36-50"] += 1
                    else: groups["50+"] += 1
                q_stats["age_groups"] = {k: {"count": v, "percent": round((v/len(ages))*100, 1)} for k, v in groups.items() if v > 0}
        else:
            all_ans = [resp.get(q_id, "") for resp in responses if resp.get(q_id, "")]
            q_stats["answers"] = all_ans[:50]
            q_stats["total_answers"] = len(all_ans)
        stats[q_id] = q_stats
    return stats

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/survey-login", methods=["GET", "POST"])
def survey_login():
    error = None
    if request.method == "POST":
        if request.form.get("token", "").strip() == SURVEY_CODE:
            session["survey_access"] = True
            return redirect(url_for("survey"))
        error = "Неверный код доступа."
    return render_template("survey_login.html", error=error)

@app.route("/survey")
def survey():
    if not session.get("survey_access"):
        return redirect(url_for("survey_login"))
    return render_template("survey.html", questions=QUESTIONS)

@app.route("/submit", methods=["POST"])
def submit():
    if not session.get("survey_access"):
        return redirect(url_for("survey_login"))
    responses = load_responses()
    answers = {}
    for q in QUESTIONS:
        q_id = str(q["id"])
        answers[q_id] = request.form.getlist(q_id) if q["type"] == "checkbox" else request.form.get(q_id, "")
    answers["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    answers["id"] = str(uuid.uuid4())[:8]
    responses.append(answers)
    save_responses(responses)
    session.pop("survey_access", None)
    return redirect(url_for("thanks"))

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password", "").strip() == ADMIN_PASSWORD:
            session["admin_access"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Неверный пароль."
    return render_template("admin_login.html", error=error)

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_access"):
        return redirect(url_for("admin_login"))
    responses = load_responses()
    stats = calculate_stats(responses)
    return render_template("admin.html", responses=responses, stats=stats, questions=QUESTIONS, total=len(responses))

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_access", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
