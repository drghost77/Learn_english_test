import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import random

# Charger données des livres (simule data.json - colle le JSON ci-dessous dans un fichier data.json)
data = {
    "books": {
        "40_lecons": {
            "lessons": [
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
                        {"type": "correction", "question": "Corrige: I am a women.", "answer": "I am a woman.", "feedback": "Orthographe 'woman'."},
                        {"type": "qcm", "question": "Je suis heureux.", "options": ["I am happy.", "I am sad.", "I am big."], "answer": 0},
                        {"type": "trous", "question": "I am ___ man.", "answer": "a", "feedback": "Article indéfini."},
                        {"type": "production", "question": "Réforme: Je suis Dan.", "answer": "I am Dan.", "feedback": "Pas d'article pour noms propres."}
                    ],
                    "orales": ["Lis à voix haute 3x: I am glad. I am sad. I am Pam.", "Discussion: Décris-toi en 3 phrases.", "Shadow: Répète après lecture: I am a man from France."]
                },
                # Ajoute plus de leçons basées sur TOC (placeholder pour les 39 autres - extrais同様)
                # Ex: Lesson 2 from p18: "Je ne suis pas" ...
                {
                    "id": 2,
                    "title": "Je ne suis pas",
                    "summary": "Négative du verbe 'to be'.",
                    "objectifs": ["Former négations.", "Vocabulaire animaux/personnes."],
                    "explications": "'I am not' pour négative. Ex: I am not big.",
                    "exercices": [ ... ]  # Similaire, ajoute 8+
                }
                # ... jusqu'à 40
            ]
        },
        "800_expressions": {
            "chapters": [
                {
                    "id": 1,
                    "title": "Pour commencer",
                    "summary": "Salutations, présentations, invitations.",
                    "objectifs": ["Saluer, présenter, inviter.", "Refuser poliment."],
                    "explications": "Hi! = Bonjour. Nice to meet you = Ravi de vous rencontrer.",
                    "exercices": [
                        {"type": "qcm", "question": "Bonjour !", "options": ["Hi!", "Bye!", "Thanks."], "answer": 0},
                        # Ajoute 8+ basés sur extraits p9-20
                        {"type": "trous", "question": "Nice to ___ you.", "answer": "meet"},
                        # etc.
                    ],
                    "orales": ["Script: Hi, I'm Pierre. Nice to meet you.", "Discussion: Présente-toi.", "Shadow: Répète invitations."]
                }
                # ... 14 chapitres
            ]
        },
        "etre_pro": {
            "fiches": [
                {
                    "id": 1,
                    "title": "Grow Your English",
                    "summary": "Autoévaluation et plan d'action.",
                    "objectifs": ["Définir objectifs GROW.", "Évaluer compétences."],
                    "explications": "G: Goal, R: Reality, O: Options, W: Will.",
                    "exercices": [
                        {"type": "production", "question": "Définis ton objectif anglais."},
                        # Questionnaires interactifs
                    ],
                    "orales": ["Lis ton plan à voix haute.", "Discussion: Tes forces en comm."]
                }
                # ... 24 fiches
            ]
        }
    },
    "srs_cards": [  # 500+ cartes 80/20
        {"front": "Je suis", "back": "I am", "interval": 1, "easiness": 2.5, "next": "2025-11-13"},
        # Vocab des livres + faux amis: actual = en fait (pas actuel), etc.
        # Phrases utiles: Hi! I'm glad.
        # Collocations: have a good time.
    ],
    "tests": {  # Quiz et paliers
        "a2": [{"question": "Traduire: Bonjour.", "answer": "Hello."}],
        # etc.
    }
}

# Session state pour progression, SRS
if 'progress' not in st.session_state:
    st.session_state.progress = {"completed": [], "score": 0}
if 'srs_queue' not in st.session_state:
    st.session_state.srs_queue = data["srs_cards"].copy()

st.title("Maîtrise l'Anglais - Site Personnel")

# Sidebar navigation
page = st.sidebar.selectbox("Sections", ["Dashboard", "40 Leçons", "800 Expressions", "Être Pro", "SRS", "Tests"])

if page == "Dashboard":
    st.header("Tableau de Bord")
    completed = len(st.session_state.progress["completed"])
    total_lessons = sum(len(book[key]) for book in data["books"].values() for key in book)
    progress = (completed / total_lessons) * 100 if total_lessons > 0 else 0
    st.progress(progress / 100)
    st.write(f"Progrès global: {progress:.1f}%")
    st.write("Badges: " + ("Survival English" if progress > 33 else ""))
    # Auto-éval CEFR simple
    level = st.slider("Ton niveau actuel (1=A1, 5=C1)", 1, 5)
    st.write(f"Niveau estimé: {'A1' if level==1 else 'A2' if level==2 else 'B1' if level==3 else 'B2' if level==4 else 'C1'}")

elif page in ["40 Leçons", "800 Expressions", "Être Pro"]:
    book_key = "40_lecons" if page == "40 Leçons" else "800_expressions" if page == "800 Expressions" else "etre_pro"
    items_key = "lessons" if book_key == "40_lecons" else "chapters" if book_key == "800_expressions" else "fiches"
    st.header(page)
    for item in data["books"][book_key][items_key]:
        with st.expander(item["title"]):
            st.write("**Résumé:** " + item["summary"])
            st.write("**Objectifs:** " + ", ".join(item["objectifs"]))
            st.write("**Explications:** " + item["explications"])
            st.subheader("Exercices")
            for ex in item["exercices"]:
                if ex["type"] == "qcm":
                    ans = st.radio(ex["question"], ex["options"])
                    if st.button("Vérifier"):
                        if ex["options"].index(ans) == ex["answer"]:
                            st.success("Correct! " + ex["feedback"])
                            st.session_state.progress["score"] += 1
                        else:
                            st.error("Faux. " + ex["feedback"])
                # Similaire pour autres types (trous: text_input, etc.)
            st.subheader("Activités orales (lis à voix haute)")
            for orale in item["orales"]:
                st.write(orale)
            if st.button("Marquer comme complété"):
                if item["id"] not in st.session_state.progress["completed"]:
                    st.session_state.progress["completed"].append(item["id"])

elif page == "SRS":
    st.header("Répétition Espacée")
    if st.session_state.srs_queue:
        card = random.choice(st.session_state.srs_queue)  # Simule scheduler
        st.write("Front: " + card["front"])
        ans = st.text_input("Ta réponse")
        if st.button("Vérifier"):
            if ans.lower() == card["back"].lower():
                st.success("Correct!")
                card["interval"] *= card["easiness"]
                card["next"] = (datetime.now() + timedelta(days=card["interval"])).strftime("%Y-%m-%d")
            else:
                st.error("Faux: " + card["back"])
                card["interval"] = 1
    else:
        st.write("Toutes cartes maîtrisées!")

elif page == "Tests":
    st.header("Tests")
    level = st.selectbox("Palier", ["A2", "B1", "B2"])
    questions = data["tests"][level.lower()]
    score = 0
    for q in questions:
        ans = st.text_input(q["question"])
        if st.button("Vérifier", key=q["question"]):
            if ans.lower() == q["answer"].lower():
                score += 1
    st.write(f"Score: {score}/{len(questions)}")

# Export
if st.sidebar.button("Export Anki CSV"):
    df = pd.DataFrame(data["srs_cards"])
    st.download_button("Télécharger", df.to_csv(index=False), "anki.csv")