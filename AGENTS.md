# LearnQUIZ — Contexte Projet

## Description
Plateforme éducative qui transforme des cours (PDF, texte, Markdown) en quiz
interactifs via l'IA (Gemini). Inclut un tuteur IA, un module Q&A et un suivi
de progression.

## Stack technique
- Frontend : React 18 + TypeScript + Vite + Zustand + React Router v6
- Backend : FastAPI (Python 3.11) + SQLAlchemy 2.0 + Alembic
- Base de données : PostgreSQL (Aiven)
- IA : Google Gemini API (gemini-1.5-pro pour quiz/résumé, gemini-1.5-flash pour Q&A)
- Auth : JWT (email/password) + Google OAuth 2.0

## Structure des ports en dev
- Frontend : http://localhost:5173
- Backend : http://localhost:8000
- Docs API : http://localhost:8000/docs

## Modules principaux
1. Auth (register, login, google oauth)
2. Courses (upload, parsing, résumé)
3. Quiz (génération, session, évaluation)
4. Tutor IA (feedback sur erreurs)
5. Q&A (chat sur un cours)
6. Progress (historique, points faibles, relations inter-cours)

## Règles spécifiques au projet
- Les appels Gemini sont tous dans `backend/app/services/gemini.py`
- Ne jamais appeler Gemini directement depuis un endpoint, toujours via le service
- Le texte extrait d'un cours est stocké en DB (raw_text) pour éviter de re-parser
- Si un texte dépasse 100 000 tokens, le chunker dans parser.py doit être utilisé
- Les quiz sont toujours au format JSON structuré (voir schéma dans services/quiz_engine.py)

## Ce qu'il NE faut PAS faire
- Ne pas modifier `alembic/env.py` sans confirmation
- Ne pas supprimer de colonnes en migration sans vérifier les données existantes
- Ne pas hardcoder de clés API (tout passe par os.getenv())
- Ne pas utiliser `response_model=None` sur les endpoints (toujours typer les réponses)

## Modèle de données
Voir le fichier `docs/schema.md` pour le schéma complet de la base de données.