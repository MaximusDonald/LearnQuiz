# LearnQuiz 🎓

LearnQuiz est une plateforme éducative innovante qui transforme vos cours (PDF, texte, Markdown) en quiz interactifs grâce à l'intelligence artificielle (Google Gemini). L'application propose également un tuteur IA, un module Q&A pour poser des questions sur vos cours, et un suivi de progression détaillé.

## 🚀 Fonctionnalités Principales

- **Génération de Quiz par IA** : Transformez instantanément vos notes ou PDF en questionnaires à choix multiples (QCM), questions vrai/faux et questions ouvertes.
- **Tuteur IA Intégré** : Obtenez des retours personnalisés et des explications détaillées lorsque vous faites des erreurs dans vos quiz.
- **Assistant Q&A** : Posez des questions directement sur le contenu de vos cours pour clarifier les concepts complexes.
- **Suivi de Progression** : Analysez vos performances, identifiez vos points faibles, et visualisez les relations entre vos différents cours.
- **Authentification Sécurisée** : Connexion classique (email/mot de passe) ou rapide via Google OAuth 2.0.

## 🛠️ Stack Technique

- **Frontend** : React 19, TypeScript, Vite, Zustand, React Router v7
- **Backend** : FastAPI (Python 3.11), SQLAlchemy 2.0, Alembic, Pydantic
- **Base de Données** : PostgreSQL
- **Intelligence Artificielle** : API Google Gemini (gemini-1.5-pro pour la génération/résumé, gemini-1.5-flash pour le Q&A)
- **Authentification** : JWT, Google OAuth 2.0

## ⚙️ Prérequis

- Node.js (v18+)
- Python (3.11+)
- PostgreSQL installé et en cours d'exécution
- Une clé API Google Gemini
- Des identifiants Google OAuth (Optionnel, pour la connexion via Google)

## 💻 Installation et Démarrage en Local

### 1. Cloner le dépôt
```bash
git clone <votre-url-github>
cd LearnQuiz
```

### 2. Base de données
Assurez-vous que PostgreSQL est lancé localement et créez une base de données vide pour le projet (ex: `learnquiz`).

### 3. Configuration de l'environnement
Copiez le fichier d'exemple et remplissez-le avec vos identifiants :
```bash
cp .env.example .env
```
*Note: Renseignez-y l'URL de votre base de données, votre clé Gemini et vos clés Google OAuth.*

### 4. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Sur Windows : venv\Scripts\activate
# Sur Linux/Mac : source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Application des migrations de la base de données
alembic upgrade head

# Démarrage du serveur
uvicorn app.main:app --reload --port 8000
```
- Le backend sera accessible sur : `http://localhost:8000`
- La documentation de l'API (Swagger UI) est sur : `http://localhost:8000/docs`

### 5. Frontend (React/Vite)
Ouvrez un nouveau terminal à la racine du projet :
```bash
cd frontend

# Installation des dépendances
npm install

# Démarrage du serveur de développement
npm run dev
```
- Le frontend sera accessible sur : `http://localhost:5173`

## ☁️ Déploiement sur Render

Ce projet est configuré pour être facilement déployé sur [Render](https://render.com/) grâce au fichier `render.yaml` (Blueprint / Infrastructure as Code) inclus à la racine du projet.

### Étapes de déploiement :
1. Poussez votre code (incluant le `render.yaml`) sur un dépôt GitHub.
2. Créez un compte sur [Render](https://render.com/).
3. Sur le dashboard, cliquez sur **New +** et sélectionnez **Blueprint**.
4. Liez votre compte GitHub et sélectionnez le dépôt `LearnQuiz`.
5. Render va analyser le `render.yaml` et créer automatiquement :
   - Une base de données PostgreSQL (`learnquiz-db`).
   - Le Web Service backend FastAPI (`learnquiz-backend`).
   - Le Web Service frontend React (`learnquiz-frontend`).
6. Pendant la création, Render vous demandera de configurer vos variables d'environnement privées (`GEMINI_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

*Avantage du Blueprint : Les connexions entre la base de données, le backend et le frontend se font automatiquement grâce aux références de variables du fichier YAML.*

## 📜 Modèle de Données
Pour plus de détails sur la structure de la base de données, consultez `docs/schema.md`.

## 📄 Licence
Ce projet est sous licence MIT.
