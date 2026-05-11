import streamlit as st
import json
import uuid
from datetime import datetime
import os

# ===== НАСТРОЙКИ =====
SURVEY_CODE = "opros-2024"
ADMIN_PASSWORD = "admin-2024"

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'responses.json')

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

# ===== CSS =====
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .block-container { background: white; border-radius: 20px; padding: 40px; margin: 20px auto; max-width: 800px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
    h1 { color: #2d3748 !important; text-align: center; }
    h2 { color: #4a5568 !important; }
    h3 { color: #2d3748 !important; }
    .stButton>button { width: 100%; padding: 15px; border-radius: 12px; font-size: 18px; font-weight: 600; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: none !important; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102,126,234,0.3); }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea { border: 2px solid #e2e8f0 !important; border-radius: 12px !important; padding: 15px !important; }
    .stRadio>div { background: #f7fafc; border-radius: 12px; padding: 10px; }
    .stCheckbox>div { background: #f7fafc; border-radius: 12px; padding: 10px; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 16px; text-align: center; }
    .stat-number { font-size: 36px; font-weight: 700; }
    .bar-bg { width: 100%; height: 20px; background: #e2e8f0; border-radius: 10px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px; }
    .answer-item { padding: 10px; border-bottom: 1px solid #e2e8f0; }
    .center { text-align: center; }
    .logo { font-size: 60px; text-align: center; }
    .icon { font-size: 40px; text-align: center; }
    .error { background: #fed7d7; color: #c53030; padding: 12px; border-radius: 10px; text-align: center; }
    .success { background: #c6f6d5; color: #22543d; padding: 12px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ===== ИНИЦИАЛИЗАЦИЯ =====
def init_session():
    defaults = {
        'page': 'home',
        'survey_access': False,
        'admin_access': False,
        'answers': {},
        'current_q': 0,
        'survey_token': '',
        'admin_pass': ''
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ===== ГЛАВНАЯ =====
if st.session_state.page == 'home':
    st.markdown('<div class="logo">🚬</div>', unsafe_allow_html=True)
    st.markdown('<h1>Опросник по теме курения</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center" style="color: #718096;">Анонимный исследовательский опрос</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
        if st.button("📝 Пройти опрос", key="btn_survey"):
            st.session_state.page = 'survey_login'
            st.session_state.survey_access = False
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="center" style="color: #718096; font-size: 14px;">У меня есть код доступа</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
        if st.button("📊 Вход для администратора", key="btn_admin"):
            st.session_state.page = 'admin_login'
            st.session_state.admin_access = False
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="center" style="color: #718096; font-size: 14px;">Просмотр результатов</p>', unsafe_allow_html=True)

# ===== ВХОД В ОПРОС =====
elif st.session_state.page == 'survey_login':
    if st.button("← На главную", key="btn_home1"):
        st.session_state.page = 'home'
        st.experimental_rerun()

    st.markdown('<div class="icon">🔑</div>', unsafe_allow_html=True)
    st.markdown('<h1>Вход в опрос</h1>', unsafe_allow_html=True)

    token = st.text_input("Код доступа", value=st.session_state.get('survey_token', ''), key="survey_token_input")

    if st.button("Войти в опрос", key="btn_survey_login"):
        if token.strip() == SURVEY_CODE:
            st.session_state.survey_access = True
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.session_state.page = 'survey'
            st.experimental_rerun()
        else:
            st.markdown('<div class="error">Неверный код доступа</div>', unsafe_allow_html=True)

# ===== ОПРОС =====
elif st.session_state.page == 'survey':
    if not st.session_state.survey_access:
        st.session_state.page = 'survey_login'
        st.experimental_rerun()

    q = QUESTIONS[st.session_state.current_q]
    progress = (st.session_state.current_q + 1) / len(QUESTIONS) * 100

    st.markdown(f'<div style="width:100%;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;margin-bottom:30px;"><div style="width:{progress}%;height:100%;background:linear-gradient(90deg, #667eea, #764ba2);border-radius:4px;"></div></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #667eea; font-weight: 600; font-size: 14px;">Вопрос {q["id"]} из {len(QUESTIONS)}</p>', unsafe_allow_html=True)
    st.markdown(f'<h3>{q["text"]}</h3>', unsafe_allow_html=True)

    q_key = f"q_{q['id']}"

    if q["type"] == "radio":
        options = q["options"]
        current_val = st.session_state.answers.get(str(q["id"]), options[0])
        answer = st.radio("", options, index=options.index(current_val) if current_val in options else 0, key=q_key)
        st.session_state.answers[str(q["id"])] = answer

    elif q["type"] == "checkbox":
        answers = []
        for i, opt in enumerate(q["options"]):
            checked = opt in st.session_state.answers.get(str(q["id"]), [])
            if st.checkbox(opt, value=checked, key=f"{q_key}_{i}"):
                answers.append(opt)
        st.session_state.answers[str(q["id"])] = answers

    elif q["type"] == "text":
        current = st.session_state.answers.get(str(q["id"]), "")
        answer = st.text_input("", value=current, placeholder=q.get("placeholder", ""), key=q_key)
        if answer:
            st.session_state.answers[str(q["id"])] = answer

    elif q["type"] == "textarea":
        current = st.session_state.answers.get(str(q["id"]), "")
        answer = st.text_area("", value=current, placeholder=q.get("placeholder", ""), key=q_key)
        if answer:
            st.session_state.answers[str(q["id"])] = answer

    elif q["type"] == "number":
        current = st.session_state.answers.get(str(q["id"]), 18)
        try:
            current_int = int(current) if current else 18
        except:
            current_int = 18
        answer = st.number_input("", min_value=10, max_value=100, value=current_int, key=q_key)
        st.session_state.answers[str(q["id"])] = str(int(answer))

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.current_q > 0:
            if st.button("← Назад", key="btn_back"):
                st.session_state.current_q -= 1
                st.experimental_rerun()

    with col2:
        if st.session_state.current_q < len(QUESTIONS) - 1:
            if st.button("Далее →", key="btn_next"):
                st.session_state.current_q += 1
                st.experimental_rerun()
        else:
            if st.button("✅ Отправить опрос", key="btn_submit"):
                responses = load_responses()
                answers = dict(st.session_state.answers)
                answers["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                answers["id"] = str(uuid.uuid4())[:8]
                responses.append(answers)
                save_responses(responses)
                st.session_state.survey_access = False
                st.session_state.answers = {}
                st.session_state.current_q = 0
                st.session_state.page = 'thanks'
                st.experimental_rerun()

# ===== СПАСИБО =====
elif st.session_state.page == 'thanks':
    st.markdown('<div style="font-size:60px;text-align:center;">🎉</div>', unsafe_allow_html=True)
    st.markdown('<h1>Спасибо за участие!</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center">Ваши ответы успешно сохранены.</p>', unsafe_allow_html=True)
    if st.button("На главную", key="btn_home2"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# ===== ВХОД АДМИНА =====
elif st.session_state.page == 'admin_login':
    if st.button("← На главную", key="btn_home3"):
        st.session_state.page = 'home'
        st.experimental_rerun()

    st.markdown('<div class="icon">🔐</div>', unsafe_allow_html=True)
    st.markdown('<h1>Вход для администратора</h1>', unsafe_allow_html=True)

    password = st.text_input("Пароль", type="password", key="admin_pass_input")

    if st.button("Войти", key="btn_admin_login"):
        if password.strip() == ADMIN_PASSWORD:
            st.session_state.admin_access = True
            st.session_state.page = 'admin'
            st.experimental_rerun()
        else:
            st.markdown('<div class="error">Неверный пароль</div>', unsafe_allow_html=True)

# ===== АДМИН-ПАНЕЛЬ =====
elif st.session_state.page == 'admin':
    if not st.session_state.admin_access:
        st.session_state.page = 'admin_login'
        st.experimental_rerun()

    responses = load_responses()
    stats = calculate_stats(responses)

    st.markdown('<h1>📊 Админ-панель</h1>', unsafe_allow_html=True)

    if st.button("Выйти", key="btn_logout"):
        st.session_state.admin_access = False
        st.session_state.page = 'home'
        st.experimental_rerun()

    st.markdown(f'<div class="stat-box"><div class="stat-number">{len(responses)}</div><div style="font-size:14px;opacity:0.9;">Всего ответов</div></div>', unsafe_allow_html=True)

    for q in QUESTIONS:
        q_id = str(q["id"])
        q_stats = stats.get(q_id, {})

        with st.expander(f"Вопрос {q['id']}: {q['text']}"):
            if q["type"] in ["radio", "checkbox"] and q_stats.get("percentages"):
                for opt in q["options"]:
                    data = q_stats["percentages"].get(opt, {"count": 0, "percent": 0})
                    st.write(f"**{opt}**: {data['count']} ({data['percent']}%)")
                    st.markdown(f'<div class="bar-bg"><div class="bar-fill" style="width: {data["percent"]}%"></div></div>', unsafe_allow_html=True)

            elif q["type"] == "number" and q_stats.get("average"):
                st.write(f"**Средний возраст:** {q_stats['average']} лет")
                st.write(f"**Минимальный:** {q_stats['min']} лет")
                st.write(f"**Максимальный:** {q_stats['max']} лет")
                if q_stats.get("age_groups"):
                    st.write("**Возрастные группы:**")
                    for group, data in q_stats["age_groups"].items():
                        st.write(f"- {group}: {data['count']} ({data['percent']}%)")

            else:
                st.write(f"**Всего ответов: {q_stats.get('total_answers', 0)}**")
                for ans in q_stats.get("answers", [])[:20]:
                    st.markdown(f'<div class="answer-item">• {ans}</div>', unsafe_allow_html=True)

    with st.expander("📋 Сырые данные (JSON)"):
        st.json(responses)
