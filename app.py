from flask import Flask, request, render_template, session, redirect, url_for
import json
import os
from anime_recommender import AnimeRecommender, UserManager  # Deine Klassen

app = Flask(__name__)
app.secret_key = 'dein_geheimer_schlüssel'  # Für Sitzungen erforderlich

# Initialisierung
user_manager = UserManager()
with open('anime_database.json', 'r', encoding='utf-8') as f:
    anime_db = json.load(f)
recommender = AnimeRecommender(anime_db)

# Routen
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('recommend'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data_file, is_admin = user_manager.login(username, password)
        if data_file:
            session['username'] = username
            session['data_file'] = data_file
            session['is_admin'] = is_admin
            return redirect(url_for('recommend'))
        return "Ungültige Anmeldedaten"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_manager.register(username, password):
            return redirect(url_for('login'))
        return "Benutzername vergeben"
    return render_template('register.html')

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Lade Benutzerdaten
    data_file = session.get('data_file')
    if data_file and os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        feedback = user_data.get('feedback', [])
    else:
        feedback = [None] * len(anime_db)
    if request.method == 'POST':
        # Beispiel: Bewertungen speichern
        ratings = {int(k): float(v) for k, v in request.form.items() if k.isdigit()}
        for idx, rating in ratings.items():
            feedback[idx] = rating
        if data_file:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump({'feedback': feedback}, f, indent=4)
        # Empfehlungen generieren (vereinfacht)
        ratings_array = [r if r is not None else float('nan') for r in feedback]
        recommendations = recommender.recommend_content(ratings_array, "Sub", set(), set(), "Egal", (0.2, 0.3, 0.2, 0.15, 0.15), top_n=5)
        return render_template('recommend.html', recommendations=recommendations, anime_db=anime_db)
    return render_template('recommend.html', feedback=feedback, anime_db=anime_db)

if __name__ == '__main__':
    app.run(debug=True)