import sys
import json
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model for Portuguese
# https://www.sbert.net/docs/pretrained_models.html?highlight=portuguese#multi-lingual-models
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()


if __name__ == "__main__":
    with open('data.json', "r", encoding='utf-8') as file:
        data = json.load(file)

    # Update each document in the JSON data
    for document in data:
        # Extract fields if they exist, otherwise default to empty strings
        title = document.get("title", "")
        content = document.get("content", "")

        combined_text = title + " " + content
        document["vector"] = get_embedding(combined_text)

    with open('data_embeddings.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
