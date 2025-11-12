# app.py
import streamlit as st
import json
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random
import os
import math
import re

# ---------------------------
# Config & chemins
# ---------------------------
DATA_FILE = "data.json"
DB_FILE = "progress.db"
APP_TITLE = "Maîtrise l'Anglais — 90 Jours (zéro dépense)"

st.set_page_config(APP_TITLE, layout="wide")

# ---------------------------
# Helpers DB
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        username TEXT,
        lesson_id INTEGER,
        book_key TEXT,
        completed_at TEXT,
        PRIMARY KEY (username, lesson_id, book_key)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS srs (
        username TEXT,
        front TEXT,
        back TEXT,
        interval REAL,
        easiness REAL,
        reps INTEGER,
        next_due TEXT,
        PRIMARY KEY (username, front)
    )""")
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# ---------------------------
# Load or create data.json
# ---------------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    # fallback minimal dataset (immediate usable)
    data = {
        "meta": {"created": datetime.now().isoformat()},
        "books": {
            "40_lecons": {"lessons": [
                {
                    "id": 1,
                    "title": "Je suis",
                    "summary": "Présentation du verbe 'to be' au présent.",
                    "objectifs": ["Maîtriser 'I am' + adjectifs.", "Comprendre genre/nombre.", "Pratiquer prononciation."],
                    "explications": "En anglais, 'Je suis' se dit 'I am'. Exemples: I am glad (Je suis content). Adjectifs invariants: sad, glad.",
                    "exercices": [
                        {"type": "qcm", "question": "Traduire: Je suis un homme.", "options": ["I am a man.", "I am man.", "I'm a men."], "answer": 0, "feedback": "Avec article 'a' pour singulier."},
                        {"type": "trous", "question": "I ___ glad.", "answer": "am", "feedback": "Forme affirmative de 'to be'."},
                        {"type": "transformation", "question": "I am sad. (négative)", "answer": "I am not sad.", "feedback": "Ajouter 'not'."},
                        {"type": "production", "question": "Écris une phrase sur toi: I am ...", "answer": "Libre", "feedback": "Vérifie grammaire."},
                        {"type": "correction", "question": "Corrige: I am a women.", "answer": "I am a woman.", "feedback": "Orthographe 'woman'."}
                    ],
                    "orales": ["Lis à voix haute 3x: I am glad. I am sad. I am Pam.", "Discussion: Décris-toi en 3 phrases.", "Shadow: Répète après lecture: I am a man from France."]
                }
            ]},
            "800_expressions": {"chapters": []},
            "etre_pro": {"fiches": []}
        },
        "srs_cards": [
            {"front": "Je suis", "back": "I am", "interval": 1, "easiness": 2.5, "next": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
        ],
        "tests": {"a2": [{"question": "Traduire: Bonjour.", "answer": "Hello."}]}
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# User handling (simple)
# ---------------------------
st.sidebar.title("Utilisateur")
username = st.sidebar.text_input("Pseudo (local)", value="default_user")
if not username:
    st.warning("Indique un pseudo pour sauvegarder ta progression locale.")
else:
    cur.execute("INSERT OR IGNORE INTO users (username, created_at) VALUES (?,?)", (username, datetime.now().isoformat()))
    conn.commit()

# ---------------------------
# Utility functions
# ---------------------------
def total_lessons_count(data):
    total = 0
    for book in data["books"].values():
        # book is dict containing a list under a key (lessons/chapters/fiches)
        for k, v in book.items():
            if isinstance(v, list):
                total += len(v)
    return total

def mark_completed(username, book_key, lesson_id):
    cur.execute("""
    INSERT OR IGNORE INTO progress (username, lesson_id, book_key, completed_at)
    VALUES (?,?,?,?)
    """, (username, lesson_id, book_key, datetime.now().isoformat()))
    conn.commit()

def is_completed(username, book_key, lesson_id):
    cur.execute("SELECT 1 FROM progress WHERE username=? AND book_key=? AND lesson_id=?", (username, book_key, lesson_id))
    return cur.fetchone() is not None

# SM-2 like scheduler for SRS
def srs_check_due(username):
    cur.execute("SELECT front, back, interval, easiness, reps, next_due FROM srs WHERE username=?", (username,))
    rows = cur.fetchall()
    due = []
    for r in rows:
        front, back, interval, easiness, reps, next_due = r
        if not next_due:
            due.append({"front": front, "back": back, "interval": interval, "easiness": easiness, "reps": reps})
        else:
            if datetime.strptime(next_due, "%Y-%m-%d").date() <= datetime.now().date():
                due.append({"front": front, "back": back, "interval": interval, "easiness": easiness, "reps": reps})
    return due

def srs_register_card(username, card):
    cur.execute("INSERT OR REPLACE INTO srs (username, front, back, interval, easiness, reps, next_due) VALUES (?,?,?,?,?,?,?)",
                (username, card["front"], card["back"], card.get("interval",1), card.get("easiness",2.5), card.get("reps",0), card.get("next", (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))))
    conn.commit()

def srs_update_after_review(username, front, quality):
    # quality 0-5
    cur.execute("SELECT interval, easiness, reps FROM srs WHERE username=? AND front=?", (username, front))
    row = cur.fetchone()
    if not row:
        return
    interval, easiness, reps = row
    # Update easiness factor
    easiness = max(1.3, easiness + 0.1 - (5-quality)*(0.08 + (5-quality)*0.02))
    if quality < 3:
        reps = 0
        interval = 1
    else:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = math.ceil(interval * easiness)
    next_due = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
    cur.execute("UPDATE srs SET interval=?, easiness=?, reps=?, next_due=? WHERE username=? AND front=?", (interval, easiness, reps, next_due, username, front))
    conn.commit()

# Simple rule-based grammar hints (fallback "Mini Coach IA")
def grammar_hints(text):
    hints = []
    # simple common patterns
    if re.search(r"\bI am a [a-z]+s\b", text, re.I):
        hints.append("Vérifie le pluriel : 'I am a men' → 'I am a man'")
    if re.search(r"\bi am\b(?=\s+[A-Z])", text):
        hints.append("Les majuscules après 'I am' sont ok pour noms propres ; vérifie la capitalisation.")
    if re.search(r"\b(to be)\b.*\bnot\b", text, re.I):
        hints.append("Bonne utilisation de 'not' pour la négation.")
    # article hints
    if re.search(r"\bI am (a|an) (hour|honor)\b", text, re.I):
        hints.append("Après 'a' vs 'an' : devant une voyelle sonore on met 'an' (ex: an hour).")
    # contraction hint
    if "I am not" in text:
        hints.append("Tu peux utiliser la contraction: I'm not ... (informel).")
    return hints

# ---------------------------
# App UI : Sidebar nav
# ---------------------------
st.title(APP_TITLE)
page = st.sidebar.selectbox("Sections", ["Dashboard", "40 Leçons", "800 Expressions", "Être Pro", "SRS", "Tests", "Importer JSON", "Export CSV"])

# ---------------------------
# Dashboard
# ---------------------------
if page == "Dashboard":
    st.header("Tableau de bord")
    total_lessons = total_lessons_count(data)
    cur.execute("SELECT COUNT(*) FROM progress WHERE username=?", (username,))
    completed = cur.fetchone()[0]
    progress_pct = (completed / total_lessons * 100) if total_lessons else 0
    st.write(f"Leçons complétées : **{completed}** / {total_lessons}")
    st.progress(min(100, progress_pct))
    st.write(f"Progrès global : **{progress_pct:.1f}%**")
    st.markdown("### Auto-évaluation CEFR (estimation rapide)")
    level = st.slider("Ton niveau actuel (1=A1, 5=C1)", 1, 5, 1)
    st.write(f"Niveau estimé : **{'A1' if level==1 else 'A2' if level==2 else 'B1' if level==3 else 'B2' if level==4 else 'C1'}**")
    st.markdown("### Mini Coach (règles rapides)")
    sample_text = st.text_area("Écris une phrase / paragraphe en anglais pour obtenir des indices:", value="I am a women.")
    if st.button("Analyser"):
        hints = grammar_hints(sample_text)
        if hints:
            for h in hints:
                st.info(h)
        else:
            st.success("Aucun problème majeur détecté. Continue !")

# ---------------------------
# Render lessons / chapters / fiches generalized
# ---------------------------
elif page in ["40 Leçons", "800 Expressions", "Être Pro"]:
    mapping = {
        "40 Leçons": ("40_lecons", "lessons"),
        "800 Expressions": ("800_expressions", "chapters"),
        "Être Pro": ("etre_pro", "fiches")
    }
    book_key, list_key = mapping[page]
    st.header(page)
    items = data["books"].get(book_key, {}).get(list_key, [])
    if not items:
        st.warning("Aucun contenu trouvé pour cette section (ajoute via data.json ou via le scraper).")
    for item in items:
        lesson_id = item.get("id", random.randint(1000,9999))
        completed_flag = is_completed(username, book_key, lesson_id)
        with st.expander(f"{item.get('title','Untitled')} {'✅' if completed_flag else ''}"):
            st.write("**Résumé:** " + item.get("summary",""))
            st.write("**Objectifs:** " + ", ".join(item.get("objectifs",[])))
            st.write("**Explications:** " + item.get("explications",""))
            st.subheader("Exercices")
            # Use a form to group exercise submit to avoid multiple identical buttons
            with st.form(key=f"form_{book_key}_{lesson_id}"):
                score = 0
                total = 0
                answers = []
                for idx, ex in enumerate(item.get("exercices",[])):
                    total += 1
                    ex_key = f"{book_key}_{lesson_id}_{idx}"
                    if ex["type"] == "qcm":
                        st.write(f"Q: {ex['question']}")
                        choice = st.radio("", ex["options"], key=ex_key)
                        answers.append(("qcm", ex, choice))
                    elif ex["type"] == "trous":
                        ans = st.text_input(ex["question"], key=ex_key)
                        answers.append(("trous", ex, ans))
                    elif ex["type"] == "transformation":
                        ans = st.text_input(ex["question"], key=ex_key)
                        answers.append(("transformation", ex, ans))
                    elif ex["type"] == "correction":
                        ans = st.text_input(ex["question"], key=ex_key)
                        answers.append(("correction", ex, ans))
                    elif ex["type"] == "production":
                        st.write(ex["question"])
                        ans = st.text_area("Ta réponse (production libre)", key=ex_key, height=80)
                        answers.append(("production", ex, ans))
                    else:
                        # unknown: show raw
                        st.write("Exercice:", ex)
                submitted = st.form_submit_button("Soumettre exercices")
                if submitted:
                    ok_count = 0
                    for typ, ex, ans in answers:
                        if typ == "qcm":
                            correct_opt = ex["options"][ex["answer"]]
                            if ans == correct_opt:
                                ok_count += 1
                                st.success(f"QCM '{ex['question']}' — Correct. {ex.get('feedback','')}")
                            else:
                                st.error(f"QCM '{ex['question']}' — Faux. Réponse: {correct_opt}. {ex.get('feedback','')}")
                        elif typ in ("trous","transformation","correction"):
                            # normalize
                            expected = str(ex.get("answer","")).strip().lower()
                            given = str(ans).strip().lower()
                            if expected and expected == given:
                                ok_count += 1
                                st.success(f"{ex['question']} — Correct. {ex.get('feedback','')}")
                            else:
                                st.error(f"{ex['question']} — Faux. Attendu: '{ex.get('answer')}'. {ex.get('feedback','')}")
                        elif typ == "production":
                            # production is free: give hints via simple grammar_hints
                            hints = grammar_hints(ans)
                            st.write("Production enregistrée. Suggestions:")
                            if hints:
                                for h in hints:
                                    st.info(h)
                            else:
                                st.success("Ok — bien rédigé pour un début!")
                            ok_count += 0  # not counted as automatic correct
                    st.write(f"Résultats auto: {ok_count}/{total} (les productions libres ne sont pas notées automatiquement)")
                    # mark lesson completed if >50% correct OR any production present
                    if total > 0 and (ok_count / total >= 0.5 or any(a[0]=="production" and a[2].strip() != "" for a in answers)):
                        mark_completed(username, book_key, lesson_id)
                        st.balloons()
                        st.success("Leçon marquée comme complétée.")

            st.subheader("Activités orales")
            for orale in item.get("orales",[]):
                st.write("- " + orale)

# ---------------------------
# SRS Page
# ---------------------------
elif page == "SRS":
    st.header("Système de Répétition Espacée (SRS)")
    st.write("Cartes locales et scheduler SM-2 (simple).")
    # import cards from data.json into DB if missing
    if st.button("Importer cartes depuis data.json"):
        for c in data.get("srs_cards", []):
            card = {
                "front": c["front"],
                "back": c["back"],
                "interval": c.get("interval",1),
                "easiness": c.get("easiness",2.5),
                "reps": c.get("reps",0),
                "next": c.get("next", (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))
            }
            srs_register_card(username, card)
        st.success("Import terminé.")
    due = srs_check_due(username)
    if due:
        st.subheader("Cartes à réviser aujourd'hui")
        card = random.choice(due)
        st.write("Front : ", card["front"])
        answer = st.text_input("Ta réponse")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Montrer la réponse"):
                st.info("Back: " + card["back"])
        with col2:
            if st.button("Correct (5)"):
                srs_update_after_review(username, card["front"], 5)
                st.success("Bon travail — carte rééchelonnée.")
        with col3:
            if st.button("Faux (2)"):
                srs_update_after_review(username, card["front"], 2)
                st.info("Carte réinitialisée à interval 1.")
    else:
        st.write("Aucune carte due aujourd'hui. Importe-en ou crée-en ci-dessous.")
    st.markdown("**Ajouter une carte**")
    with st.form("add_card"):
        front = st.text_input("Front (mot/phrase)")
        back = st.text_input("Back (traduction/réponse)")
        if st.form_submit_button("Ajouter carte"):
            if front and back:
                srs_register_card(username, {"front":front,"back":back,"interval":1,"easiness":2.5,"reps":0,"next":(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")})
                st.success("Carte ajoutée.")

# ---------------------------
# Tests
# ---------------------------
elif page == "Tests":
    st.header("Tests & Palier")
    level_map = {"A2": "a2", "B1":"b1", "B2":"b2"}
    selected = st.selectbox("Palier", ["A2","B1","B2"])
    questions = data.get("tests",{}).get(level_map[selected], [])
    if not questions:
        st.warning("Pas encore de questions pour ce palier.")
    score = 0
    total = len(questions)
    for i, q in enumerate(questions):
        ans = st.text_input(q["question"], key=f"test_{i}")
        if st.button("Vérifier", key=f"check_{i}"):
            if ans.strip().lower() == q["answer"].strip().lower():
                st.success("Correct")
            else:
                st.error("Faux — attendu: " + q["answer"])

# ---------------------------
# Import / Export
# ---------------------------
elif page == "Importer JSON":
    st.header("Importer un fichier data.json (structure correcte requise)")
    uploaded = st.file_uploader("Choisir un data.json", type="json")
    if uploaded:
        new = json.load(uploaded)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new, f, ensure_ascii=False, indent=2)
        st.success("data.json mis à jour — redémarre l'app si nécessaire.")
elif page == "Export CSV":
    st.header("Export des cartes SRS (CSV)")
    cur.execute("SELECT front, back, interval, easiness, reps, next_due FROM srs WHERE username=?", (username,))
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["front","back","interval","easiness","reps","next_due"])
    st.download_button("Télécharger CSV SRS", df.to_csv(index=False), "srs_export.csv")

# Cleanup: commit DB
conn.commit()
