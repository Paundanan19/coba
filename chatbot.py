from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from difflib import get_close_matches

app = Flask(__name__)

# 1. Membaca Data CSV
file_path = "eco_event.csv"  # Ganti dengan path file Anda
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: File {file_path} tidak ditemukan. Pastikan file ada di direktori yang benar.")
    exit()

# 2. Pilih kolom yang relevan
if 'event_name' not in data.columns or 'event_about' not in data.columns:
    print("Error: Kolom yang dibutuhkan tidak ditemukan dalam file CSV.")
    exit()

data_subset = data[['event_name', 'event_about']].copy()
data_subset['processed_event_about'] = data_subset['event_about'].apply(simple_preprocess)

# 3. Muat model Word2Vec
model_path = "word2vec_event.model"
try:
    word2vec_model = Word2Vec.load(model_path)
except FileNotFoundError:
    print(f"Error: Model {model_path} tidak ditemukan. Pastikan model telah dilatih dan disimpan.")
    exit()

# 4. Fungsi untuk memberikan saran berdasarkan kesamaan ejaan
def get_suggestions(user_input, data):
    event_names = data['event_name'].tolist()
    suggestions = get_close_matches(user_input, event_names, n=3, cutoff=0.6)
    return suggestions

# 5. Fungsi untuk mendapatkan acara yang relevan
def get_most_relevant_event(user_input, model, data):
    input_tokens = simple_preprocess(user_input)
    input_vectors = [model.wv[token] for token in input_tokens if token in model.wv]
    
    if not input_vectors:
        suggestions = get_suggestions(user_input, data)
        if suggestions:
            return "Tidak ditemukan", f"Mungkin yang Anda maksud: {', '.join(suggestions)}"
        return "Tidak ditemukan", "Maaf, tidak ada kata yang dikenali dalam input Anda."
    
    input_vector = np.mean(input_vectors, axis=0)
    
    scores = []
    for _, row in data.iterrows():
        event_about_tokens = row['processed_event_about']
        event_vectors = [model.wv[token] for token in event_about_tokens if token in model.wv]
        
        if not event_vectors:
            scores.append(-1)
            continue
        
        event_vector = np.mean(event_vectors, axis=0)
        similarity = np.dot(input_vector, event_vector) / (np.linalg.norm(input_vector) * np.linalg.norm(event_vector))
        scores.append(similarity)
    
    if max(scores) == -1:
        suggestions = get_suggestions(user_input, data)
        if suggestions:
            return "Tidak ditemukan", f"Mungkin yang Anda maksud: {', '.join(suggestions)}"
        return "Tidak ditemukan", "Maaf, tidak ada kecocokan yang ditemukan."
    
    best_match_index = np.argmax(scores)
    best_event = data.iloc[best_match_index]
    
    return best_event['event_name'], best_event['event_about']

# 6. Halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# 7. API untuk menerima pertanyaan pengguna
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("question")
    event_name, event_about = get_most_relevant_event(user_input, word2vec_model, data_subset)
    
    response = {
        "event_name": event_name,
        "event_about": event_about
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
