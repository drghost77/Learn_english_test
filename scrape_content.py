# scrape_content.py
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import os

OUT = "data.json"

HEADERS = {"User-Agent": "90days-English-Bot (+https://github.com/ton-repo) - utilisation éducative"}

# exemples de pages sources (choisir manuellement, préférer pages CC / permises)
SOURCES = [
    # BBC Learning English short lessons (exemple)
    "https://www.bbc.co.uk/learningenglish/english/features/pronunciation",
    # Simple English Wikipedia (page category example)
    "https://simple.wikipedia.org/wiki/Category:Basic_English"
]

def fetch_text(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    # heuristic: grab main text paragraphs
    paragraphs = soup.select("article p, .story-body p, #content p, p")
    text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
    return text[:5000]  # truncate long pages

def safe_extract():
    collected = {"books": {"40_lecons": {"lessons": []}, "800_expressions": {"chapters": []}, "etre_pro": {"fiches": []}}, "srs_cards": [], "tests": {}}
    id_counter = 1000
    for src in SOURCES:
        print("Fetching", src)
        txt = fetch_text(src)
        if not txt:
            print("-> échec")
            continue
        # create a lesson
        lesson = {
            "id": id_counter,
            "title": f"Source importée: {urlparse(src).netloc}",
            "summary": "Import automatique (vérifier et modifier).",
            "objectifs": ["Lecture", "Vocabulaire"],
            "explications": txt[:1000],
            "exercices": [
                {"type":"production", "question":"Écris un résumé de ce texte en anglais (3 phrases)."},
                {"type":"trous", "question":"Remplis le trou: ...", "answer": ""}
            ],
            "orales": ["Lis le texte à voix haute pendant 3 minutes."]
        }
        collected["books"]["40_lecons"]["lessons"].append(lesson)
        id_counter += 1
        time.sleep(1)
    # merge with existing data.json if exists
    if os.path.exists(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            base = json.load(f)
    else:
        base = collected
    # simple merge: extend list
    base_books = base.get("books", {})
    for k in collected["books"]:
        key_list_name = list(collected["books"][k].keys())[0]
        base_list = base_books.get(k, {}).get(key_list_name, [])
        base_list.extend(collected["books"][k][key_list_name])
        if k not in base_books:
            base_books[k] = {key_list_name: collected["books"][k][key_list_name]}
        else:
            base_books[k][key_list_name] = base_list
    base["books"] = base_books
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)
    print("Import terminé. Vérifie data.json puis redéploie l'app si nécessaire.")

if __name__ == "__main__":
    safe_extract()
