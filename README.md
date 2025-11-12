# 🇬🇧 Maîtrise l'Anglais en 90 Jours

Application d'apprentissage de l'anglais progressive et interactive, utilisant **Streamlit** avec suivi de progression, système de répétition espacée (SRS), et exercices interactifs.

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Guide de contribution](#-guide-de-contribution)
- [FAQ](#-faq)

---

## ✨ Fonctionnalités

### 📚 Contenu pédagogique

- **40 Leçons progressives** (A1 → B2)
  - Explications claires
  - Vocabulaire contextualisé
  - Exercices variés (QCM, textes à trous, transformations, productions)
  - Activités orales guidées

- **800 Expressions courantes**
  - Classées par thème (salutations, restaurant, shopping, etc.)
  - Contexte d'utilisation
  - Variations et alternatives

- **Anglais professionnel**
  - Emails formels
  - Réunions
  - Appels téléphoniques
  - Vocabulaire spécialisé

### 🎯 Outils d'apprentissage

- **Système SRS (Spaced Repetition System)**
  - Algorithme SM-2 pour optimiser la mémorisation
  - Révisions espacées intelligentes
  - Suivi personnalisé de chaque carte

- **Suivi de progression**
  - Dashboard avec statistiques
  - Historique des leçons complétées
  - Score par exercice
  - Export CSV

- **Mini Coach Grammatical**
  - Analyse automatique de tes phrases
  - Suggestions en temps réel
  - Détection d'erreurs courantes

- **Tests de niveau**
  - Évaluation A2, B1, B2
  - Questions variées
  - Feedback immédiat

---

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Clone ou télécharge le projet**

```bash
git clone <ton-repo>
cd anglais-90-jours
```

2. **Installe les dépendances**

```bash
pip install -r requirements.txt
```

3. **Vérifie que les fichiers sont présents**

```
📁 projet/
├── app.py
├── data.json
├── scrape_content.py
├── requirements.txt
└── README.md
```

4. **Lance l'application**

```bash
streamlit run app.py
```

5. **Ouvre ton navigateur**

L'application s'ouvre automatiquement à l'adresse : `http://localhost:8501`

---

## 📖 Utilisation

### 1️⃣ Première connexion

1. Entre ton **pseudo** dans la barre latérale
2. Ta progression sera sauvegardée localement dans `progress.db`

### 2️⃣ Navigation

**Dashboard** 📊
- Vue d'ensemble de ta progression
- Auto-évaluation de niveau (A1-C1)
- Mini coach grammatical

**40 Leçons** 📖
- Leçons progressives avec exercices
- Validation automatique
- Feedback instantané

**800 Expressions** 💬
- Expressions classées par thème
- Contextes d'utilisation

**Être Pro** 💼
- Vocabulaire professionnel
- Guides pratiques (emails, réunions)

**SRS** 🔄
- Cartes à réviser quotidiennement
- Système de répétition espacée
- Ajout de nouvelles cartes

**Tests** 📝
- Tests de niveau (A2, B1, B2)
- Évaluation de tes connaissances

**Import/Export** 📥📤
- Importer un nouveau `data.json`
- Exporter ta progression en CSV

### 3️⃣ Compléter une leçon

1. Clique sur une leçon non complétée
2. Lis les **explications** et le **vocabulaire**
3. Fais les **exercices** (tous types)
4. Clique sur **"Soumettre les exercices"**
5. Obtiens ton **score** et des **feedbacks**
6. Si score ≥ 50% → leçon **complétée** ✅

### 4️⃣ Utiliser le SRS

1. Va dans **SRS** 🔄
2. Importe les cartes depuis `data.json` (1ère fois)
3. Révise les cartes dues aujourd'hui
4. Évalue ta réponse :
   - ❌ **Difficile (0)** → carte réinitialisée
   - 🤔 **Moyen (3)** → intervalle modéré
   - ✅ **Facile (5)** → intervalle maximal
5. Ajoute tes propres cartes personnalisées

---

## 📁 Structure du projet

### Fichiers principaux

```
📄 app.py                  # Application Streamlit principale
📄 data.json               # Base de données du contenu pédagogique
📄 scrape_content.py       # Script d'enrichissement de contenu
📄 requirements.txt        # Dépendances Python
📄 README.md               # Documentation (ce fichier)
📄 progress.db             # Base SQLite (généré automatiquement)
```

### Architecture de `app.py`

Le code est **modulaire** et organisé en **classes** :

```python
DatabaseManager         # Gestion de la base de données SQLite
DataManager            # Chargement/sauvegarde de data.json
GrammarAnalyzer        # Analyse grammaticale simple

# Fonctions de rendu
render_sidebar()       # Barre latérale utilisateur
render_dashboard()     # Tableau de bord
render_lesson()        # Affichage d'une leçon
render_srs_page()      # Page SRS
render_tests_page()    # Page tests
```

### Structure de `data.json`

```json
{
  "meta": {...},
  "books": {
    "40_lecons": {
      "lessons": [
        {
          "id": 1,
          "title": "...",
          "level": "A1",
          "explications": "...",
          "vocabulaire": [...],
          "exercices": [...],
          "orales": [...]
        }
      ]
    },
    "800_expressions": {
      "chapters": [...]
    },
    "etre_pro": {
      "fiches": [...]
    }
  },
  "srs_cards": [...],
  "tests": {...}
}
```

---

## 🛠️ Guide de contribution

### Ajouter du contenu manuellement

#### Méthode 1 : Via `scrape_content.py`

```bash
python scrape_content.py
```

Menu interactif :
1. Vocabulaire de base → ajoute des cartes SRS
2. Leçons de grammaire → ajoute dans "40 Leçons"
3. Fiches pro → ajoute dans "Être Pro"
4. Expressions → ajoute dans "800 Expressions"
5. Tout ajouter → ajoute tout d'un coup

#### Méthode 2 : Modifier `data.json` directement

1. Ouvre `data.json` dans un éditeur
2. Ajoute tes leçons/expressions/cartes
3. Respecte la structure JSON
4. Sauvegarde et relance l'app

**Exemple : Ajouter une leçon**

```json
{
  "id": 5,
  "title": "Leçon 5 : Les Pronoms",
  "level": "A1",
  "summary": "Apprendre les pronoms personnels",
  "objectifs": ["Maîtriser I/you/he/she..."],
  "explications": "Les pronoms en anglais...",
  "vocabulaire": [
    {"word": "I", "translation": "je"},
    {"word": "you", "translation": "tu/vous"}
  ],
  "exercices": [
    {
      "type": "qcm",
      "question": "Comment dit-on 'il' ?",
      "options": ["he", "she", "it"],
      "answer": 0,
      "feedback": "'he' = il (masculin)"
    }
  ],
  "orales": ["Prononce les pronoms"]
}
```

### Types d'exercices disponibles

| Type | Description | Validation |
|------|-------------|------------|
| `qcm` | Questions à choix multiples | Automatique |
| `trous` | Texte à trous | Automatique |
| `transformation` | Transformer une phrase | Automatique |
| `correction` | Corriger une erreur | Automatique |
| `production` | Production libre | Suggestions IA |

### Personnaliser le Mini Coach

Édite la classe `GrammarAnalyzer` dans `app.py` :

```python
class GrammarAnalyzer:
    @staticmethod
    def analyze(text):
        hints = []
        
        # Ajoute tes règles personnalisées
        if "règle détectée" in text:
            hints.append("💡 Ton conseil ici")
        
        return hints
```

---

## 🔧 Personnalisation avancée

### Changer le thème Streamlit

Crée un fichier `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

### Ajouter une nouvelle section

1. Ajoute une clé dans `data.json` :

```json
"books": {
  "ma_section": {
    "title": "Ma Section",
    "lessons": []
  }
}
```

2. Dans `app.py`, ajoute dans le menu :

```python
pages = {
    "📚 Ma Section": "ma_section"
}
```

3. Crée une fonction de rendu si besoin

---

## ❓ FAQ

### 1. Mes données sont-elles sauvegardées ?

✅ **Oui**, localement :
- **Progression** : `progress.db` (SQLite)
- **Contenu** : `data.json`
- Aucune donnée n'est envoyée en ligne

### 2. Puis-je utiliser l'app sur plusieurs appareils ?

Oui, copie les fichiers `progress.db` et `data.json` entre appareils.

### 3. Comment réinitialiser ma progression ?

Supprime le fichier `progress.db` et relance l'app.

### 4. L'app est-elle hors ligne ?

L'app fonctionne hors ligne, sauf si tu utilises `scrape_content.py` pour du scraping web.

### 5. Puis-je ajouter de l'audio ?

Pour l'instant, non. Mais tu peux ajouter des liens YouTube/Forvo dans les leçons.

### 6. Y a-t-il une limite de cartes SRS ?

Non, illimité ! L'algorithme SM-2 gère efficacement des milliers de cartes.

### 7. Comment exporter mes cartes vers Anki ?

Utilise l'export CSV, puis importe dans Anki avec le bon mapping des colonnes.

### 8. Le Mini Coach utilise-t-il une vraie IA ?

Non, c'est un système **basé sur des règles** (regex). Tu peux l'améliorer en ajoutant tes règles.

### 9. Puis-je partager `data.json` avec d'autres ?

✅ Oui ! C'est fait pour. Partage-le et chacun aura le même contenu.

### 10. Comment contribuer au projet ?

- Ajoute du contenu dans `data.json`
- Améliore le code (`app.py`)
- Crée des scrapers dans `scrape_content.py`
- Propose des améliorations (issues GitHub)

---

## 📊 Statistiques du contenu

**Actuellement inclus** (après enrichissement complet) :

- ✅ **4 leçons** de grammaire (A1)
- ✅ **60+ cartes SRS** de vocabulaire de base
- ✅ **4 chapitres** d'expressions (salutations, présentations, restaurant, shopping)
- ✅ **3 fiches** professionnelles (emails, réunions, appels)
- ✅ Tests de niveau A2/B1

**Objectif final** :
- 📚 40 leçons complètes
- 💬 800 expressions
- 💼 20+ fiches pro
- 🔄 500+ cartes SRS

---

## 🎯 Roadmap

### Version actuelle : 2.0

- [x] Refonte complète du code
- [x] Architecture modulaire
- [x] Système SRS fonctionnel
- [x] Mini coach grammatical
- [x] Export/Import

### Prochaines versions

**v2.1** (Contenu)
- [ ] Compléter les 40 leçons
- [ ] Ajouter 800 expressions
- [ ] Tests B2/C1

**v2.2** (Fonctionnalités)
- [ ] Graphiques de progression
- [ ] Statistiques détaillées
- [ ] Badges/Récompenses
- [ ] Mode "Défi 90 jours"

**v2.3** (Avancé)
- [ ] Intégration API de prononciation
- [ ] Reconnaissance vocale
- [ ] Mode multi-utilisateurs
- [ ] Synchronisation cloud (optionnelle)

---

## 📝 Licence

Ce projet est **open source** et libre d'utilisation.

Partage, modifie, améliore ! 🚀

---

## 🙏 Remerciements

Merci d'utiliser cette application ! 

Si elle t'aide dans ton apprentissage, partage-la avec d'autres apprenants. 💙

---

## 📞 Contact & Support

- 🐛 **Bugs** : Crée une issue sur GitHub
- 💡 **Suggestions** : Ouvre une discussion
- ❓ **Questions** : Consulte la FAQ ci-dessus

---

**Bon apprentissage ! 🎉🇬🇧**

*"The journey of a thousand miles begins with a single step."*
