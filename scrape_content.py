"""
Script de scraping pour enrichir automatiquement data.json
Ajoute du contenu depuis diverses sources web
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_FILE = Path("data.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# =============================================================================
# UTILITAIRES
# =============================================================================

def load_data():
    """Charge le fichier data.json"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_data(data):
    """Sauvegarde dans data.json"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Données sauvegardées dans {DATA_FILE}")

def fetch_page(url):
    """Récupère le contenu HTML d'une page"""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"❌ Erreur lors du fetch de {url}: {e}")
        return None

# =============================================================================
# SCRAPERS SPÉCIFIQUES
# =============================================================================

def scrape_basic_vocabulary():
    """
    Génère une liste de vocabulaire de base (A1-A2)
    (Exemple avec données hardcodées - à adapter selon tes besoins)
    """
    
    print("📚 Génération de vocabulaire de base...")
    
    vocab_categories = {
        "Salutations": [
            {"en": "Hello", "fr": "Bonjour", "level": "A1"},
            {"en": "Good morning", "fr": "Bonjour (matin)", "level": "A1"},
            {"en": "Good evening", "fr": "Bonsoir", "level": "A1"},
            {"en": "Good night", "fr": "Bonne nuit", "level": "A1"},
            {"en": "Goodbye", "fr": "Au revoir", "level": "A1"},
            {"en": "See you later", "fr": "À plus tard", "level": "A1"},
        ],
        "Présentations": [
            {"en": "My name is...", "fr": "Je m'appelle...", "level": "A1"},
            {"en": "I am from...", "fr": "Je viens de...", "level": "A1"},
            {"en": "Nice to meet you", "fr": "Enchanté(e)", "level": "A1"},
            {"en": "How are you?", "fr": "Comment vas-tu ?", "level": "A1"},
            {"en": "I'm fine, thank you", "fr": "Je vais bien, merci", "level": "A1"},
        ],
        "Nombres": [
            {"en": "one", "fr": "un", "level": "A1"},
            {"en": "two", "fr": "deux", "level": "A1"},
            {"en": "three", "fr": "trois", "level": "A1"},
            {"en": "ten", "fr": "dix", "level": "A1"},
            {"en": "twenty", "fr": "vingt", "level": "A1"},
            {"en": "hundred", "fr": "cent", "level": "A1"},
        ],
        "Couleurs": [
            {"en": "red", "fr": "rouge", "level": "A1"},
            {"en": "blue", "fr": "bleu", "level": "A1"},
            {"en": "green", "fr": "vert", "level": "A1"},
            {"en": "yellow", "fr": "jaune", "level": "A1"},
            {"en": "black", "fr": "noir", "level": "A1"},
            {"en": "white", "fr": "blanc", "level": "A1"},
        ],
        "Famille": [
            {"en": "mother", "fr": "mère", "level": "A1"},
            {"en": "father", "fr": "père", "level": "A1"},
            {"en": "brother", "fr": "frère", "level": "A1"},
            {"en": "sister", "fr": "sœur", "level": "A1"},
            {"en": "son", "fr": "fils", "level": "A1"},
            {"en": "daughter", "fr": "fille", "level": "A1"},
        ],
    }
    
    # Convertir en cartes SRS
    srs_cards = []
    for category, words in vocab_categories.items():
        for word in words:
            srs_cards.append({
                "front": word["fr"],
                "back": word["en"],
                "category": category,
                "level": word["level"]
            })
    
    print(f"✅ {len(srs_cards)} cartes de vocabulaire générées")
    return srs_cards

def generate_grammar_lessons():
    """
    Génère des leçons de grammaire structurées
    """
    
    print("📖 Génération de leçons de grammaire...")
    
    lessons = [
        {
            "id": 3,
            "title": "Leçon 3 : Les Articles (a, an, the)",
            "level": "A1",
            "summary": "Maîtriser l'utilisation des articles en anglais",
            "objectifs": [
                "Différencier 'a' et 'an'",
                "Comprendre l'usage de 'the'",
                "Savoir quand ne pas mettre d'article"
            ],
            "explications": """Les articles en anglais :

1. **A** (un/une) - devant une consonne
   - a book (un livre)
   - a car (une voiture)
   - a university (une université) *attention au son*

2. **AN** (un/une) - devant une voyelle SONORE
   - an apple (une pomme)
   - an hour (une heure) *le 'h' est muet*
   - an elephant (un éléphant)

3. **THE** (le/la/les) - article défini
   - the book (le livre)
   - the sun (le soleil) *objet unique*
   - the United States (les États-Unis) *noms de pays pluriels*

⚠️ Pas d'article :
- I like music. (J'aime la musique)
- She speaks English. (Elle parle anglais)
- We eat breakfast. (Nous prenons le petit-déjeuner)""",
            "vocabulaire": [
                {"word": "apple", "translation": "pomme", "example": "I eat an apple."},
                {"word": "book", "translation": "livre", "example": "This is a book."},
                {"word": "hour", "translation": "heure", "example": "Wait an hour."},
                {"word": "sun", "translation": "soleil", "example": "The sun is bright."}
            ],
            "exercices": [
                {
                    "type": "qcm",
                    "question": "Choisis l'article correct : I have ___ dog.",
                    "options": ["a", "an", "the"],
                    "answer": 0,
                    "feedback": "'Dog' commence par une consonne → 'a'"
                },
                {
                    "type": "trous",
                    "question": "She is ___ engineer.",
                    "answer": "an",
                    "feedback": "'Engineer' commence par une voyelle → 'an'"
                },
                {
                    "type": "correction",
                    "question": "Corrige : I ate a orange.",
                    "answer": "I ate an orange.",
                    "feedback": "Devant 'orange' (voyelle) → 'an'"
                },
                {
                    "type": "transformation",
                    "question": "Ajoute l'article : ___ Eiffel Tower is in Paris.",
                    "answer": "The Eiffel Tower is in Paris.",
                    "feedback": "Monument unique → 'the'"
                }
            ],
            "orales": [
                "Répète : a book, an apple, the sun",
                "Trouve 5 mots qui prennent 'an'",
                "Décris ta chambre en utilisant les articles"
            ]
        },
        {
            "id": 4,
            "title": "Leçon 4 : Le Présent Simple",
            "level": "A1",
            "summary": "Formation et usage du présent simple",
            "objectifs": [
                "Conjuguer au présent simple",
                "Comprendre 's' à la 3e personne",
                "Former des questions et négations"
            ],
            "explications": """Le présent simple exprime :
- Des habitudes : I work every day.
- Des vérités générales : The sun rises in the east.
- Des goûts : She likes chocolate.

**Formation affirmative :**
- I/You/We/They + verbe
- He/She/It + verbe + S

Exemples :
- I work / He works
- You play / She plays
- We eat / It eats

**Négation :**
- I/You/We/They + don't + verbe
- He/She/It + doesn't + verbe

**Questions :**
- Do + I/you/we/they + verbe ?
- Does + he/she/it + verbe ?""",
            "vocabulaire": [
                {"word": "work", "translation": "travailler", "example": "I work in Paris."},
                {"word": "play", "translation": "jouer", "example": "She plays tennis."},
                {"word": "like", "translation": "aimer", "example": "He likes music."},
                {"word": "eat", "translation": "manger", "example": "We eat pasta."}
            ],
            "exercices": [
                {
                    "type": "trous",
                    "question": "She ___ (play) piano.",
                    "answer": "plays",
                    "feedback": "3e personne singulier → ajouter 's'"
                },
                {
                    "type": "transformation",
                    "question": "I like coffee. (négation)",
                    "answer": "I don't like coffee.",
                    "alternatives": ["I do not like coffee."],
                    "feedback": "don't + verbe à l'infinitif"
                },
                {
                    "type": "qcm",
                    "question": "___ he work here?",
                    "options": ["Do", "Does", "Is"],
                    "answer": 1,
                    "feedback": "3e personne singulier → Does"
                }
            ],
            "orales": [
                "Conjugue 'to work' à toutes les personnes",
                "Parle de ta routine quotidienne",
                "Pose 3 questions à un(e) camarade"
            ]
        }
    ]
    
    print(f"✅ {len(lessons)} leçons générées")
    return lessons

def generate_professional_fiches():
    """Génère des fiches professionnelles"""
    
    print("💼 Génération de fiches professionnelles...")
    
    fiches = [
        {
            "id": 2,
            "title": "Réunion Professionnelle",
            "domaine": "Communication orale",
            "niveau": "B1",
            "phrases_cles": [
                {"en": "Let's get started.", "fr": "Commençons.", "context": "Début de réunion"},
                {"en": "Could you please clarify?", "fr": "Pourriez-vous clarifier ?", "context": "Demander des précisions"},
                {"en": "I agree with you.", "fr": "Je suis d'accord avec vous.", "context": "Accord"},
                {"en": "I'm afraid I disagree.", "fr": "Je ne suis pas d'accord.", "context": "Désaccord poli"},
                {"en": "Let me think about it.", "fr": "Laissez-moi y réfléchir.", "context": "Temporiser"},
                {"en": "That's a good point.", "fr": "C'est un bon point.", "context": "Valider une idée"},
                {"en": "To sum up...", "fr": "En résumé...", "context": "Synthèse"}
            ],
            "vocabulaire": [
                {"word": "meeting", "translation": "réunion"},
                {"word": "agenda", "translation": "ordre du jour"},
                {"word": "deadline", "translation": "date limite"},
                {"word": "feedback", "translation": "retour/commentaire"},
                {"word": "proposal", "translation": "proposition"}
            ],
            "conseils": [
                "Arrivez 5 minutes en avance",
                "Éteignez votre téléphone",
                "Prenez des notes",
                "Posez des questions si besoin",
                "Utilisez un langage formel"
            ]
        },
        {
            "id": 3,
            "title": "Appels Téléphoniques Professionnels",
            "domaine": "Communication orale",
            "niveau": "B1",
            "structure": [
                {
                    "etape": "Répondre",
                    "exemples": [
                        "Good morning, [Company name], [Your name] speaking.",
                        "Hello, this is [Name]. How can I help you?"
                    ]
                },
                {
                    "etape": "Demander quelqu'un",
                    "exemples": [
                        "Could I speak to Mr. Smith, please?",
                        "I'd like to talk to the manager, please."
                    ]
                },
                {
                    "etape": "Transférer",
                    "exemples": [
                        "Please hold, I'll transfer you.",
                        "Let me put you through to the sales department."
                    ]
                },
                {
                    "etape": "Prendre un message",
                    "exemples": [
                        "Can I take a message?",
                        "Would you like to leave a message?"
                    ]
                },
                {
                    "etape": "Terminer",
                    "exemples": [
                        "Thank you for calling.",
                        "Have a great day!"
                    ]
                }
            ]
        }
    ]
    
    print(f"✅ {len(fiches)} fiches professionnelles générées")
    return fiches

def add_expressions_chapter():
    """Ajoute un chapitre d'expressions"""
    
    print("💬 Génération de chapitre d'expressions...")
    
    chapters = [
        {
            "id": 3,
            "title": "Au Restaurant",
            "theme": "Food & Dining",
            "expressions": [
                {
                    "en": "Can I see the menu, please?",
                    "fr": "Puis-je voir le menu, s'il vous plaît ?",
                    "context": "Demander le menu"
                },
                {
                    "en": "I'd like to order...",
                    "fr": "Je voudrais commander...",
                    "context": "Commander"
                },
                {
                    "en": "What do you recommend?",
                    "fr": "Que recommandez-vous ?",
                    "context": "Demander conseil"
                },
                {
                    "en": "Can I have the bill, please?",
                    "fr": "L'addition, s'il vous plaît ?",
                    "context": "Demander l'addition",
                    "variations": ["Check, please!", "Could we get the check?"]
                },
                {
                    "en": "It was delicious!",
                    "fr": "C'était délicieux !",
                    "context": "Compliment"
                },
                {
                    "en": "I'm allergic to...",
                    "fr": "Je suis allergique à...",
                    "context": "Allergie alimentaire"
                }
            ]
        },
        {
            "id": 4,
            "title": "Shopping",
            "theme": "Shopping",
            "expressions": [
                {
                    "en": "How much is this?",
                    "fr": "Combien ça coûte ?",
                    "context": "Demander le prix"
                },
                {
                    "en": "Can I try it on?",
                    "fr": "Puis-je l'essayer ?",
                    "context": "Vêtements"
                },
                {
                    "en": "Do you have this in a different size?",
                    "fr": "Avez-vous ceci dans une autre taille ?",
                    "context": "Taille"
                },
                {
                    "en": "I'm just looking, thanks.",
                    "fr": "Je regarde seulement, merci.",
                    "context": "Refuser de l'aide poliment"
                },
                {
                    "en": "Can I pay by card?",
                    "fr": "Puis-je payer par carte ?",
                    "context": "Paiement"
                }
            ]
        }
    ]
    
    print(f"✅ {len(chapters)} chapitres d'expressions générés")
    return chapters

# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================

def main():
    """Fonction principale d'enrichissement"""
    
    print("=" * 60)
    print("🚀 ENRICHISSEMENT DE data.json")
    print("=" * 60)
    
    # Charger les données existantes
    data = load_data()
    
    if not data:
        print("❌ Fichier data.json introuvable. Crée-le d'abord avec l'app.")
        return
    
    print(f"\n📂 Fichier data.json chargé")
    
    # Menu d'options
    print("\n📋 Que veux-tu ajouter ?")
    print("1. Vocabulaire de base (cartes SRS)")
    print("2. Nouvelles leçons de grammaire")
    print("3. Fiches professionnelles")
    print("4. Chapitres d'expressions")
    print("5. Tout ajouter")
    print("0. Quitter")
    
    choice = input("\nTon choix (0-5) : ").strip()
    
    # Traiter le choix
    if choice == "1":
        new_cards = scrape_basic_vocabulary()
        data["srs_cards"].extend(new_cards)
        save_data(data)
    
    elif choice == "2":
        new_lessons = generate_grammar_lessons()
        data["books"]["40_lecons"]["lessons"].extend(new_lessons)
        save_data(data)
    
    elif choice == "3":
        new_fiches = generate_professional_fiches()
        data["books"]["etre_pro"]["fiches"].extend(new_fiches)
        save_data(data)
    
    elif choice == "4":
        new_chapters = add_expressions_chapter()
        data["books"]["800_expressions"]["chapters"].extend(new_chapters)
        save_data(data)
    
    elif choice == "5":
        print("\n🔄 Ajout de tout le contenu...")
        
        # Vocabulaire
        new_cards = scrape_basic_vocabulary()
        data["srs_cards"].extend(new_cards)
        
        # Leçons
        new_lessons = generate_grammar_lessons()
        data["books"]["40_lecons"]["lessons"].extend(new_lessons)
        
        # Fiches pro
        new_fiches = generate_professional_fiches()
        data["books"]["etre_pro"]["fiches"].extend(new_fiches)
        
        # Expressions
        new_chapters = add_expressions_chapter()
        data["books"]["800_expressions"]["chapters"].extend(new_chapters)
        
        save_data(data)
        print("\n✅ Tout le contenu a été ajouté !")
    
    elif choice == "0":
        print("👋 Au revoir !")
        return
    
    else:
        print("❌ Choix invalide")
    
    print("\n" + "=" * 60)
    print("✅ ENRICHISSEMENT TERMINÉ")
    print("=" * 60)
    print("\n💡 Relance l'application Streamlit pour voir les changements !")

if __name__ == "__main__":
    main()
