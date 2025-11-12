"""
Application Streamlit pour l'apprentissage de l'anglais
Méthode 90 jours - Version 2.0 Refactorisée
"""

import streamlit as st
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import random
import math
import re

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_FILE = Path("data.json")
DB_FILE = Path("progress.db")
APP_TITLE = "🇬🇧 Maîtrise l'Anglais en 90 Jours"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CLASSE : GESTIONNAIRE DE BASE DE DONNÉES
# =============================================================================

class DatabaseManager:
    """Gère toutes les opérations de base de données"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = self.conn.cursor()
        
        # Table des utilisateurs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                created_at TEXT,
                current_level TEXT DEFAULT 'A1'
            )
        """)
        
        # Table de progression
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                username TEXT,
                book_key TEXT,
                lesson_id INTEGER,
                completed_at TEXT,
                score INTEGER,
                PRIMARY KEY (username, book_key, lesson_id)
            )
        """)
        
        # Table SRS (Spaced Repetition System)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS srs_cards (
                username TEXT,
                front TEXT,
                back TEXT,
                interval REAL DEFAULT 1,
                easiness REAL DEFAULT 2.5,
                repetitions INTEGER DEFAULT 0,
                next_review TEXT,
                last_review TEXT,
                PRIMARY KEY (username, front)
            )
        """)
        
        self.conn.commit()
    
    def create_user(self, username):
        """Crée un nouvel utilisateur"""
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (username, created_at) VALUES (?, ?)",
            (username, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def mark_lesson_complete(self, username, book_key, lesson_id, score=0):
        """Marque une leçon comme complétée"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO progress 
            (username, book_key, lesson_id, completed_at, score)
            VALUES (?, ?, ?, ?, ?)
        """, (username, book_key, lesson_id, datetime.now().isoformat(), score))
        self.conn.commit()
    
    def is_lesson_completed(self, username, book_key, lesson_id):
        """Vérifie si une leçon est complétée"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 1 FROM progress 
            WHERE username=? AND book_key=? AND lesson_id=?
        """, (username, book_key, lesson_id))
        return cur.fetchone() is not None
    
    def get_user_stats(self, username):
        """Récupère les statistiques de l'utilisateur"""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM progress WHERE username=?",
            (username,)
        )
        completed = cur.fetchone()[0]
        return {"completed_lessons": completed}
    
    def get_due_cards(self, username):
        """Récupère les cartes SRS à réviser aujourd'hui"""
        cur = self.conn.cursor()
        today = datetime.now().date().isoformat()
        cur.execute("""
            SELECT front, back, interval, easiness, repetitions 
            FROM srs_cards 
            WHERE username=? AND (next_review IS NULL OR next_review <= ?)
        """, (username, today))
        
        cards = []
        for row in cur.fetchall():
            cards.append({
                "front": row[0],
                "back": row[1],
                "interval": row[2],
                "easiness": row[3],
                "repetitions": row[4]
            })
        return cards
    
    def add_srs_card(self, username, front, back):
        """Ajoute une nouvelle carte SRS"""
        cur = self.conn.cursor()
        next_review = (datetime.now() + timedelta(days=1)).date().isoformat()
        cur.execute("""
            INSERT OR REPLACE INTO srs_cards 
            (username, front, back, next_review, last_review)
            VALUES (?, ?, ?, ?, ?)
        """, (username, front, back, next_review, datetime.now().isoformat()))
        self.conn.commit()
    
    def update_srs_card(self, username, front, quality):
        """
        Met à jour une carte SRS après révision
        quality: 0-5 (0=échec total, 5=parfait)
        Utilise l'algorithme SM-2
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT interval, easiness, repetitions 
            FROM srs_cards WHERE username=? AND front=?
        """, (username, front))
        
        row = cur.fetchone()
        if not row:
            return
        
        interval, easiness, reps = row
        
        # Calcul du nouveau facteur d'aisance (SM-2)
        easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Si la réponse est incorrecte (quality < 3)
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
        
        # Calculer la prochaine date de révision
        next_review = (datetime.now() + timedelta(days=interval)).date().isoformat()
        
        cur.execute("""
            UPDATE srs_cards 
            SET interval=?, easiness=?, repetitions=?, 
                next_review=?, last_review=?
            WHERE username=? AND front=?
        """, (interval, easiness, reps, next_review, datetime.now().isoformat(), username, front))
        
        self.conn.commit()

# =============================================================================
# CLASSE : GESTIONNAIRE DE DONNÉES
# =============================================================================

class DataManager:
    """Gère le chargement et la sauvegarde des données JSON"""
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        if not self.data_file.exists():
            return self.create_default_data()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement de {self.data_file}: {e}")
            return self.create_default_data()
    
    def create_default_data(self):
        """Crée une structure de données par défaut"""
        default_data = {
            "meta": {
                "version": "2.0",
                "created": datetime.now().isoformat()
            },
            "books": {
                "40_lecons": {"title": "40 Leçons", "lessons": []},
                "800_expressions": {"title": "800 Expressions", "chapters": []},
                "etre_pro": {"title": "Être Pro", "fiches": []}
            },
            "srs_cards": [],
            "tests": {}
        }
        self.save_data(default_data)
        return default_data
    
    def save_data(self, data):
        """Sauvegarde les données dans le fichier JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_total_lessons_count(self):
        """Compte le nombre total de leçons"""
        total = 0
        for book in self.data["books"].values():
            for key, value in book.items():
                if isinstance(value, list):
                    total += len(value)
        return total

# =============================================================================
# CLASSE : ANALYSEUR GRAMMATICAL
# =============================================================================

class GrammarAnalyzer:
    """Analyse simple de grammaire pour feedback"""
    
    @staticmethod
    def analyze(text):
        """Analyse un texte et retourne des suggestions"""
        hints = []
        
        # Vérification du pluriel avec 'I am a'
        if re.search(r"\bI am a \w+s\b", text, re.I):
            hints.append("⚠️ Attention au pluriel : après 'a', utilise le singulier (ex: 'a man' pas 'a mans')")
        
        # Vérification de la majuscule sur 'I'
        if re.search(r"\bi\b(?!\s+am\b)", text):
            hints.append("💡 'I' (je) prend toujours une majuscule en anglais")
        
        # Vérification article a/an
        if re.search(r"\ba [aeiou]", text, re.I):
            hints.append("💡 Devant une voyelle, utilise 'an' au lieu de 'a' (ex: 'an apple')")
        
        # Vérification négation
        if re.search(r"\bam not\b|\bare not\b|\bis not\b", text, re.I):
            hints.append("✅ Bonne utilisation de la forme négative !")
        
        # Vérification forme contractée
        if "I am" in text and "I'm" not in text:
            hints.append("💡 Tu peux utiliser la forme contractée : I'm (plus naturel à l'oral)")
        
        return hints

# =============================================================================
# INTERFACE UTILISATEUR
# =============================================================================

def render_sidebar(db):
    """Affiche la barre latérale avec gestion utilisateur"""
    st.sidebar.title("👤 Utilisateur")
    
    username = st.sidebar.text_input(
        "Ton pseudo",
        value=st.session_state.get("username", ""),
        placeholder="Entre ton pseudo..."
    )
    
    if username:
        st.session_state["username"] = username
        db.create_user(username)
        
        # Afficher les stats
        stats = db.get_user_stats(username)
        st.sidebar.success(f"✅ Connecté : **{username}**")
        st.sidebar.metric("Leçons complétées", stats["completed_lessons"])
    else:
        st.sidebar.warning("⚠️ Entre un pseudo pour sauvegarder ta progression")
    
    st.sidebar.markdown("---")
    return username

def render_dashboard(db, data_manager, username):
    """Affiche le tableau de bord"""
    st.title("📊 Tableau de Bord")
    
    # Statistiques globales
    col1, col2, col3 = st.columns(3)
    
    stats = db.get_user_stats(username)
    total_lessons = data_manager.get_total_lessons_count()
    progress_pct = (stats["completed_lessons"] / total_lessons * 100) if total_lessons > 0 else 0
    
    with col1:
        st.metric("📚 Leçons complétées", f"{stats['completed_lessons']} / {total_lessons}")
    
    with col2:
        st.metric("📈 Progression", f"{progress_pct:.1f}%")
    
    with col3:
        due_cards = len(db.get_due_cards(username))
        st.metric("🔄 Cartes à réviser", due_cards)
    
    # Barre de progression
    st.progress(min(1.0, progress_pct / 100))
    
    st.markdown("---")
    
    # Auto-évaluation CEFR
    st.subheader("🎯 Auto-évaluation de niveau")
    
    level_descriptions = {
        "A1": "Débutant - Je comprends des phrases simples",
        "A2": "Élémentaire - Je peux communiquer sur des sujets familiers",
        "B1": "Intermédiaire - Je peux raconter des expériences",
        "B2": "Intermédiaire avancé - Je peux argumenter",
        "C1": "Avancé - Je m'exprime couramment"
    }
    
    selected_level = st.select_slider(
        "Ton niveau actuel",
        options=list(level_descriptions.keys()),
        format_func=lambda x: f"{x} - {level_descriptions[x]}"
    )
    
    st.info(f"📌 Niveau sélectionné : **{selected_level}** - {level_descriptions[selected_level]}")
    
    st.markdown("---")
    
    # Mini coach grammatical
    st.subheader("🤖 Mini Coach Grammatical")
    st.write("Écris une phrase en anglais pour obtenir des conseils instantanés :")
    
    sample_text = st.text_area(
        "Ta phrase",
        placeholder="Exemple : I am a students.",
        height=100
    )
    
    if st.button("✨ Analyser"):
        if sample_text.strip():
            hints = GrammarAnalyzer.analyze(sample_text)
            
            if hints:
                st.write("**Suggestions :**")
                for hint in hints:
                    st.write(hint)
            else:
                st.success("✅ Aucun problème majeur détecté ! Continue comme ça ! 🎉")
        else:
            st.warning("⚠️ Entre une phrase pour l'analyser")

def render_exercise(exercise, idx, key_prefix):
    """Affiche un exercice selon son type"""
    
    st.markdown(f"**Exercice {idx + 1}** - Type : *{exercise['type']}*")
    
    user_answer = None
    
    if exercise["type"] == "qcm":
        st.write(exercise["question"])
        user_answer = st.radio(
            "Choisis ta réponse :",
            exercise["options"],
            key=f"{key_prefix}_qcm_{idx}"
        )
        
    elif exercise["type"] == "trous":
        user_answer = st.text_input(
            exercise["question"],
            key=f"{key_prefix}_trous_{idx}",
            placeholder="Ta réponse..."
        )
        
    elif exercise["type"] == "transformation":
        st.write(exercise["question"])
        user_answer = st.text_input(
            "Ta transformation :",
            key=f"{key_prefix}_transfo_{idx}",
            placeholder="Écris ta réponse..."
        )
        
    elif exercise["type"] == "correction":
        st.write(exercise["question"])
        user_answer = st.text_input(
            "Phrase corrigée :",
            key=f"{key_prefix}_correction_{idx}",
            placeholder="Corrige la phrase..."
        )
        
    elif exercise["type"] == "production":
        st.write(exercise["question"])
        user_answer = st.text_area(
            "Ta production :",
            key=f"{key_prefix}_production_{idx}",
            height=100,
            placeholder="Écris ta réponse..."
        )
    
    return user_answer

def check_exercise(exercise, user_answer):
    """Vérifie la réponse d'un exercice"""
    
    if exercise["type"] == "qcm":
        correct_answer = exercise["options"][exercise["answer"]]
        is_correct = (user_answer == correct_answer)
        
        return {
            "correct": is_correct,
            "feedback": exercise.get("feedback", ""),
            "expected": correct_answer
        }
    
    elif exercise["type"] in ["trous", "transformation", "correction"]:
        expected = str(exercise["answer"]).strip().lower()
        given = str(user_answer).strip().lower()
        
        # Vérifier aussi les alternatives si elles existent
        alternatives = exercise.get("alternatives", [])
        is_correct = (given == expected) or (given in [alt.strip().lower() for alt in alternatives])
        
        return {
            "correct": is_correct,
            "feedback": exercise.get("feedback", ""),
            "expected": exercise["answer"]
        }
    
    elif exercise["type"] == "production":
        # Pour les productions libres, on utilise l'analyseur grammatical
        hints = GrammarAnalyzer.analyze(user_answer)
        
        return {
            "correct": None,  # Pas de correction auto
            "feedback": exercise.get("feedback", ""),
            "hints": hints
        }
    
    return {"correct": False, "feedback": "Type d'exercice non reconnu"}

def render_lesson(lesson, book_key, db, username):
    """Affiche une leçon complète"""
    
    lesson_id = lesson["id"]
    is_completed = db.is_lesson_completed(username, book_key, lesson_id)
    
    # En-tête de la leçon
    status_icon = "✅" if is_completed else "📝"
    
    with st.expander(f"{status_icon} {lesson['title']}", expanded=not is_completed):
        
        # Informations de la leçon
        st.markdown(f"**Niveau :** {lesson.get('level', 'N/A')}")
        st.markdown(f"**Résumé :** {lesson.get('summary', '')}")
        
        # Objectifs
        if "objectifs" in lesson:
            st.markdown("**🎯 Objectifs :**")
            for obj in lesson["objectifs"]:
                st.markdown(f"- {obj}")
        
        # Explications
        if "explications" in lesson:
            with st.expander("📖 Explications", expanded=True):
                st.markdown(lesson["explications"])
        
        # Vocabulaire
        if "vocabulaire" in lesson and lesson["vocabulaire"]:
            with st.expander("📚 Vocabulaire"):
                for vocab in lesson["vocabulaire"]:
                    st.markdown(f"- **{vocab['word']}** : {vocab['translation']}")
                    if "example" in vocab:
                        st.markdown(f"  *Exemple : {vocab['example']}*")
        
        # Exercices
        if "exercices" in lesson and lesson["exercices"]:
            st.markdown("---")
            st.subheader("✍️ Exercices")
            
            # Stocker les réponses
            if f"answers_{lesson_id}" not in st.session_state:
                st.session_state[f"answers_{lesson_id}"] = {}
            
            # Afficher chaque exercice
            for idx, exercise in enumerate(lesson["exercices"]):
                user_answer = render_exercise(exercise, idx, f"{book_key}_{lesson_id}")
                st.session_state[f"answers_{lesson_id}"][idx] = (exercise, user_answer)
                st.markdown("---")
            
            # Bouton de soumission
            if st.button(f"✅ Soumettre les exercices", key=f"submit_{lesson_id}"):
                answers = st.session_state[f"answers_{lesson_id}"]
                
                correct_count = 0
                total_count = 0
                
                st.markdown("### 📝 Résultats :")
                
                for idx, (exercise, user_answer) in answers.items():
                    result = check_exercise(exercise, user_answer)
                    
                    if result["correct"] is True:
                        correct_count += 1
                        total_count += 1
                        st.success(f"✅ Exercice {idx + 1} : Correct ! {result['feedback']}")
                    
                    elif result["correct"] is False:
                        total_count += 1
                        st.error(f"❌ Exercice {idx + 1} : Incorrect")
                        st.info(f"💡 Réponse attendue : **{result['expected']}**")
                        st.write(result['feedback'])
                    
                    else:  # Production libre
                        st.info(f"📝 Exercice {idx + 1} : Production libre enregistrée")
                        if result.get("hints"):
                            st.write("**Suggestions :**")
                            for hint in result["hints"]:
                                st.write(hint)
                
                # Score final
                if total_count > 0:
                    score_pct = (correct_count / total_count) * 100
                    st.markdown(f"### 🎯 Score : {correct_count}/{total_count} ({score_pct:.0f}%)")
                    
                    # Marquer comme complétée si > 50%
                    if score_pct >= 50:
                        db.mark_lesson_complete(username, book_key, lesson_id, score=int(score_pct))
                        st.balloons()
                        st.success("🎉 Leçon complétée ! Bravo !")
                    else:
                        st.warning("💪 Continue ! Refais les exercices pour atteindre 50% minimum.")
        
        # Activités orales
        if "orales" in lesson and lesson["orales"]:
            with st.expander("🎤 Activités Orales"):
                for oral in lesson["orales"]:
                    st.markdown(f"- {oral}")

def render_book_content(book_key, data, db, username):
    """Affiche le contenu d'un livre"""
    
    book = data["books"].get(book_key, {})
    
    # Déterminer la clé de contenu
    content_key = None
    if "lessons" in book:
        content_key = "lessons"
    elif "chapters" in book:
        content_key = "chapters"
    elif "fiches" in book:
        content_key = "fiches"
    
    if not content_key:
        st.warning("📭 Aucun contenu disponible pour ce livre.")
        return
    
    items = book[content_key]
    
    if not items:
        st.info("📭 Ce livre ne contient pas encore de contenu. Ajoute-en via data.json !")
        return
    
    st.write(f"**{len(items)}** {content_key} disponible(s)")
    
    # Afficher chaque item
    for item in items:
        if content_key == "lessons":
            render_lesson(item, book_key, db, username)
        else:
            # Pour chapters et fiches, affichage simplifié
            st.subheader(item.get("title", "Sans titre"))
            st.write(item)

def render_srs_page(db, data_manager, username):
    """Affiche la page SRS (Répétition Espacée)"""
    
    st.title("🔄 Système de Répétition Espacée (SRS)")
    
    st.markdown("""
    Le SRS t'aide à mémoriser efficacement en espaçant les révisions.
    Plus tu connais une carte, moins souvent tu la verras !
    """)
    
    # Import depuis data.json
    if st.button("📥 Importer les cartes depuis data.json"):
        cards_imported = 0
        for card in data_manager.data.get("srs_cards", []):
            db.add_srs_card(username, card["front"], card["back"])
            cards_imported += 1
        st.success(f"✅ {cards_imported} carte(s) importée(s) !")
    
    st.markdown("---")
    
    # Cartes à réviser
    due_cards = db.get_due_cards(username)
    
    if due_cards:
        st.subheader(f"📚 {len(due_cards)} carte(s) à réviser aujourd'hui")
        
        # Sélectionner une carte aléatoire
        if "current_srs_card" not in st.session_state or st.session_state.get("srs_refresh", False):
            st.session_state["current_srs_card"] = random.choice(due_cards)
            st.session_state["srs_show_answer"] = False
            st.session_state["srs_refresh"] = False
        
        card = st.session_state["current_srs_card"]
        
        # Afficher la carte
        st.markdown("### Question :")
        st.info(f"**{card['front']}**")
        
        user_answer = st.text_input("Ta réponse :", key="srs_answer")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("👁️ Voir la réponse"):
                st.session_state["srs_show_answer"] = True
        
        if st.session_state.get("srs_show_answer", False):
            st.markdown("### Réponse correcte :")
            st.success(f"**{card['back']}**")
            
            st.markdown("**Comment as-tu trouvé cette carte ?**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("❌ Difficile (0)"):
                    db.update_srs_card(username, card["front"], 0)
                    st.session_state["srs_refresh"] = True
                    st.rerun()
            
            with col2:
                if st.button("🤔 Moyen (3)"):
                    db.update_srs_card(username, card["front"], 3)
                    st.session_state["srs_refresh"] = True
                    st.rerun()
            
            with col3:
                if st.button("✅ Facile (5)"):
                    db.update_srs_card(username, card["front"], 5)
                    st.session_state["srs_refresh"] = True
                    st.rerun()
    
    else:
        st.success("🎉 Aucune carte à réviser aujourd'hui ! Profites-en pour ajouter du nouveau contenu.")
    
    st.markdown("---")
    
    # Ajouter une nouvelle carte
    st.subheader("➕ Ajouter une nouvelle carte")
    
    with st.form("add_srs_card"):
        front = st.text_input("Face (français)", placeholder="Bonjour")
        back = st.text_input("Dos (anglais)", placeholder="Hello")
        
        if st.form_submit_button("➕ Ajouter"):
            if front and back:
                db.add_srs_card(username, front, back)
                st.success("✅ Carte ajoutée avec succès !")
            else:
                st.error("❌ Remplis les deux champs !")

def render_tests_page(data_manager):
    """Affiche la page des tests de niveau"""
    
    st.title("📝 Tests de Niveau")
    
    tests = data_manager.data.get("tests", {})
    
    if not tests:
        st.info("📭 Aucun test disponible pour le moment.")
        return
    
    # Sélection du niveau
    test_levels = list(tests.keys())
    selected_level = st.selectbox(
        "Choisis un niveau",
        test_levels,
        format_func=lambda x: x.upper()
    )
    
    test_data = tests[selected_level]
    
    st.subheader(test_data.get("title", f"Test {selected_level.upper()}"))
    
    if "duree" in test_data:
        st.info(f"⏱️ Durée estimée : {test_data['duree']}")
    
    questions = test_data.get("questions", [])
    
    if not questions:
        st.warning("Ce test ne contient pas encore de questions.")
        return
    
    st.markdown("---")
    
    score = 0
    total = len(questions)
    
    for idx, question in enumerate(questions):
        st.markdown(f"**Question {idx + 1}/{total}**")
        st.write(question["question"])
        
        user_answer = st.text_input(
            "Ta réponse :",
            key=f"test_{selected_level}_{idx}"
        )
        
        if st.button("Vérifier", key=f"check_{selected_level}_{idx}"):
            expected = question["answer"].strip().lower()
            given = user_answer.strip().lower()
            
            alternatives = question.get("alternatives", [])
            
            if given == expected or given in [alt.strip().lower() for alt in alternatives]:
                st.success("✅ Correct !")
                score += 1
            else:
                st.error(f"❌ Incorrect. Réponse attendue : **{question['answer']}**")
        
        st.markdown("---")

def render_import_page(data_manager):
    """Page d'import de fichier JSON"""
    
    st.title("📥 Importer un fichier JSON")
    
    st.markdown("""
    Tu peux importer un nouveau fichier `data.json` pour remplacer le contenu actuel.
    
    ⚠️ **Attention :** Cela écrasera toutes les données actuelles !
    """)
    
    uploaded_file = st.file_uploader("Choisis un fichier JSON", type=["json"])
    
    if uploaded_file:
        try:
            new_data = json.load(uploaded_file)
            
            # Aperçu des données
            st.subheader("📋 Aperçu du fichier")
            st.json(new_data.get("meta", {}))
            
            if st.button("✅ Confirmer l'import"):
                data_manager.save_data(new_data)
                data_manager.data = new_data
                st.success("✅ Fichier importé avec succès ! Recharge la page.")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de l'import : {e}")

def render_export_page(db, username):
    """Page d'export CSV"""
    
    st.title("📤 Exporter tes données")
    
    st.markdown("### 📊 Export des cartes SRS")
    
    cur = db.conn.cursor()
    cur.execute("""
        SELECT front, back, interval, easiness, repetitions, next_review, last_review
        FROM srs_cards WHERE username=?
    """, (username,))
    
    rows = cur.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=[
            "Front", "Back", "Interval", "Easiness", 
            "Repetitions", "Next Review", "Last Review"
        ])
        
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name=f"srs_cards_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 Aucune carte SRS à exporter.")
    
    st.markdown("---")
    st.markdown("### 📈 Export de la progression")
    
    cur.execute("""
        SELECT book_key, lesson_id, completed_at, score
        FROM progress WHERE username=?
        ORDER BY completed_at DESC
    """, (username,))
    
    progress_rows = cur.fetchall()
    
    if progress_rows:
        progress_df = pd.DataFrame(progress_rows, columns=[
            "Book", "Lesson ID", "Completed At", "Score"
        ])
        
        st.dataframe(progress_df)
        
        progress_csv = progress_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger Progression CSV",
            data=progress_csv,
            file_name=f"progress_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 Aucune progression à exporter.")

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Fonction principale de l'application"""
    
    # Initialiser les managers
    db = DatabaseManager(DB_FILE)
    data_manager = DataManager(DATA_FILE)
    
    # Sidebar et gestion utilisateur
    username = render_sidebar(db)
    
    if not username:
        st.warning("👈 Entre ton pseudo dans la barre latérale pour commencer !")
        st.stop()
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.title("📚 Navigation")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "📖 40 Leçons": "40_lecons",
        "💬 800 Expressions": "800_expressions",
        "💼 Être Pro": "etre_pro",
        "🔄 SRS": "srs",
        "📝 Tests": "tests",
        "📥 Importer JSON": "import",
        "📤 Exporter CSV": "export"
    }
    
    selected_page = st.sidebar.radio("Sections", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Afficher la page sélectionnée
    if page_key == "dashboard":
        render_dashboard(db, data_manager, username)
    
    elif page_key in ["40_lecons", "800_expressions", "etre_pro"]:
        book_title = data_manager.data["books"][page_key].get("title", selected_page)
        st.title(f"📚 {book_title}")
        render_book_content(page_key, data_manager.data, db, username)
    
    elif page_key == "srs":
        render_srs_page(db, data_manager, username)
    
    elif page_key == "tests":
        render_tests_page(data_manager)
    
    elif page_key == "import":
        render_import_page(data_manager)
    
    elif page_key == "export":
        render_export_page(db, username)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 À propos")
    st.sidebar.info("""
    **Maîtrise l'Anglais en 90 jours**
    
    Version 2.0 - Refactorisée
    
    Méthode progressive avec :
    - 40 leçons structurées
    - 800 expressions courantes
    - Vocabulaire professionnel
    - Système SRS intelligent
    - Tests de niveau
    """)

if __name__ == "__main__":
    main()
