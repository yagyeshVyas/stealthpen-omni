import random
import re
import time
import json
import os

SYNONYM_DB_PATH = "data/synonym_db.json"

def load_synonym_db():
    if os.path.exists(SYNONYM_DB_PATH):
        with open(SYNONYM_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "utilize": ["use", "employ", "apply"],
            "commence": ["start", "begin", "initiate"],
            "important": ["crucial", "vital", "essential", "key"],
            "difficult": ["hard", "tough", "challenging"],
            "beautiful": ["gorgeous", "stunning", "lovely"],
            "quickly": ["fast", "rapidly", "swiftly"],
            "therefore": ["so", "thus", "hence"],
            "however": ["but", "yet", "though"],
        }

FILLERS = [
    "you know,", "I mean,", "actually,", "well,", "sort of,",
    "kind of,", "to be honest,", "frankly,", "in my view,",
]

TYPO_MAP = {
    "the": ["teh", "th3"],
    "and": ["nad", "&"],
    "for": ["fro", "4"],
    "was": ["wuz", "wos"],
    "you": ["u", "ya"],
    "are": ["r", "ar"],
}

def inject_human_noise(words):
    if len(words) < 20: return words
    if random.random() < 0.15:
        pos = random.randint(5, len(words)-5)
        words.insert(pos, random.choice(FILLERS))
    typo_count = 0
    for i in range(len(words)):
        if typo_count >= 2: break
        word_clean = re.sub(r'[^\w]', '', words[i].lower())
        if word_clean in TYPO_MAP and random.random() < 0.08:
            typo_choice = random.choice(TYPO_MAP[word_clean])
            if words[i][0].isupper():
                typo_choice = typo_choice.capitalize()
            words[i] = re.sub(r'\b' + re.escape(word_clean) + r'\b', typo_choice, words[i], flags=re.IGNORECASE)
            typo_count += 1
    if len(words) > 10 and random.random() < 0.2:
        idx = random.randint(1, len(words)-2)
        words[idx], words[idx+1] = words[idx+1], words[idx]
    return words

def synonym_swap(text):
    db = load_synonym_db()
    words = text.split()
    new_words = []
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        synonyms = db.get(clean_word, [])
        if synonyms and random.random() < 0.3:
            synonym = random.choice(synonyms)
            if word[0].isupper():
                synonym = synonym.capitalize()
            punct = re.search(r'[^\w]+$', word)
            if punct:
                synonym += punct.group(0)
            new_words.append(synonym)
        else:
            new_words.append(word)
    return ' '.join(new_words)

def vary_sentence_structure(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    modified = []
    for sent in sentences:
        if len(sent.split()) > 25 and random.random() < 0.6:
            parts = re.split(r',\s+(?=[a-z])', sent)
            if len(parts) > 1:
                if len(parts) > 3 and random.random() < 0.5:
                    mid = parts[1:-1]
                    random.shuffle(mid)
                    parts = [parts[0]] + mid + [parts[-1]]
                sent = '. '.join(parts) + '.'
        elif len(sent.split()) < 8 and random.random() < 0.3 and modified:
            modified[-1] = modified[-1].rstrip('.!?') + ', ' + sent.lower()
            continue
        if random.random() < 0.2:
            endings = ['!', '...', '?', '.']
            sent = re.sub(r'[.!?]+\s*$', random.choice(endings) + ' ', sent)
        modified.append(sent)
    return ' '.join(modified)

def entropy_pipeline(text):
    techniques = [synonym_swap, vary_sentence_structure]
    random.shuffle(techniques)
    result = text
    for technique in techniques:
        if random.random() > 0.1:
            result = technique(result)
    words = result.split()
    words = inject_human_noise(words)
    result = ' '.join(words)
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s+([,.!?;:])', r'\1', result)
    return result.strip()

def humanize_text(text):
    random.seed(time.time_ns() + random.randint(0, 999999))
    iterations = random.randint(1, 3)
    result = text
    for _ in range(iterations):
        result = entropy_pipeline(result)
    return result