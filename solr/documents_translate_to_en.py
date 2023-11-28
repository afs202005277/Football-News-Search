import json
from deep_translator import GoogleTranslator


def translate_to_english(text):
    return GoogleTranslator(source='pt', target='en').translate(text)


def save_translations(translations, file_path='translations.json'):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(translations, file, ensure_ascii=False, indent=4)


def load_translations(file_path='translations.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def load_data():
    f = open('./data.json', 'r').read()
    return json.loads(f)


def translate_document(document):
    doc_id = document["id"]
    if doc_id not in translations:
        title_en = translate_to_english(document['title'][:4999])
        content_en = translate_to_english(document["content"][:4999])
        translations[doc_id] = {"title": title_en, "content": content_en}
    else:
        title_en = translations[doc_id]['title']
        content_en = translations[doc_id]['content']

    return title_en, content_en


translations = load_translations()


def translate_data():
    data = load_data()

    import time
    from datetime import timedelta

    b = time.time()
    for ind, document in enumerate(data):
        try:
            translate_document(document)
            print(
                f"{round(((ind + 1) / len(data)) * 10000) / 100}% - {timedelta(seconds=((time.time() - b) / (ind + 1) * len(data)))}")
        except:
            save_translations(translations)
            print("CRASHED")

    save_translations(translations)
