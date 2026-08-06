import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

english_stops = set(stopwords.words('english'))
german_stops = set(stopwords.words('german'))
french_stops = set(stopwords.words('french'))
spanish_stops = set(stopwords.words('spanish'))
italian_stops = set(stopwords.words('italian'))

def robust_detect_language(text):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return 'English', 1
    
    # Non-Latin characters
    if re.search(r'[\u4e00-\u9fff]', text): return 'Chinese', 0
    if re.search(r'[\u3040-\u30ff]', text): return 'Japanese', 0
    if re.search(r'[\uac00-\ud7af]', text): return 'Korean', 0
    if re.search(r'[\u0400-\u04ff]', text): return 'Russian', 0
    
    tokens = set(re.findall(r'\b[a-z\u00c0-\u024f]+\b', text.lower()))
    if len(tokens) == 0:
        return 'English', 1
        
    en_cnt = len(tokens.intersection(english_stops))
    de_cnt = len(tokens.intersection(german_stops))
    fr_cnt = len(tokens.intersection(french_stops))
    es_cnt = len(tokens.intersection(spanish_stops))
    it_cnt = len(tokens.intersection(italian_stops))
    
    # German specific triggers
    de_triggers = {'der', 'die', 'das', 'und', 'ist', 'mit', 'sehr', 'schön', 'war', 'fliegen', 'ausflug', 'rundflug', 'erlebnis', 'wir', 'uns', 'den', 'dem'}
    es_triggers = {'el', 'la', 'los', 'las', 'que', 'muy', 'excelente', 'con', 'para', 'sin', 'una', 'del', 'por', 'sobre', 'inolvidable'}
    fr_triggers = {'le', 'la', 'les', 'du', 'et', 'est', 'très', 'pour', 'une', 'des', 'avec', 'vol', 'magnifique', 'dans', 'plus'}
    
    de_trig_cnt = len(tokens.intersection(de_triggers))
    es_trig_cnt = len(tokens.intersection(es_triggers))
    fr_trig_cnt = len(tokens.intersection(fr_triggers))
    
    if de_cnt > en_cnt or de_trig_cnt >= 2:
        return 'German', 0
    if es_cnt > en_cnt or es_trig_cnt >= 2:
        return 'Spanish', 0
    if fr_cnt > en_cnt or fr_trig_cnt >= 2:
        return 'French', 0
    if it_cnt > en_cnt:
        return 'Italian', 0
        
    if en_cnt == 0 and len(tokens) >= 5:
        return 'Other Non-English', 0
        
    return 'English', 1

# Test on problematic reviews
sample_texts = [
    "Es war toll von Oben den Grand Canyon zu sehen, es wirkt ganz anders auf Fotos wie in Real. Der Pilot war ein guter Flieger und sehr nett und offen.",
    "Preis Leistung ist in Ordnung und man fliegt wirklich voll 40-45min und nicht nur 10min wie die Helis.",
    "Vielen Dank an das K2-Team! Vielen Dank nochmal, der Ausflug ist wirklich zu empfehlen!",
    "Muy profesionales y amables, sin duda, avionetas pequeñas y el piloto genial.",
    "I have a terrible fear of flying but I was desperate to be able to do this tour."
]

for t in sample_texts:
    lang, is_en = robust_detect_language(t)
    print(f"Detected: {lang:<12} (is_english={is_en}) | Text: \"{t[:70]}...\"")
