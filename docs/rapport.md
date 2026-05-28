# Audit Technique du Projet LearnQuiz

## 1. Analyse Technique & État Actuel

### Vue d'ensemble de l'architecture
Le projet suit une architecture full-stack moderne, bien découpée, qui respecte globalement les standards établis :
- **Backend** : Structuré proprement avec FastAPI (Python 3.11). L'organisation sépare clairement les responsabilités (routers dans `api/`, logique métier dans `services/`, modèles de DB dans `models/`, validation via Pydantic dans `schemas/`, et configuration dans `core/`).
- **Frontend** : Application monopage React 19 développée avec Vite, TypeScript, et Zustand. L'organisation du code source (`src/components`, `src/pages`, `src/store`) est logique. Le style s'appuie sur des modules CSS (`CSS Modules`), évitant les conflits de nommage.

### Fonctionnement global de l'application
Le flux de données décrit dans la documentation (`docs/achitechture.txt`) est bien suivi : upload du document via React, récupération et parsing avec FastAPI, stockage en base via SQLAlchemy 2.0, et exploitation de Gemini via le service dédié `services/gemini.py`. 

### État de fonctionnement du code
- **Ce qui marche** : 
  - La structure de base (authentification, gestion des cours, interactions Q&A, relations inter-cours).
  - La centralisation des appels Gemini via `gemini.py` est bien gérée (gestion asynchrone, fallback, parsing JSON).
  - L'upload et l'extraction des cours sont branchés.
- **Ce qui ne marche pas / ce qui est partiel** : 
  - Le module **Tutor IA** semble inachevé : le fichier `backend/app/api/tutor.py` est pratiquement vide (simple commentaire).
  - La couverture de **tests** est insuffisante. Le dossier `backend/tests/` ne contient qu'un modeste `test_auth.py`. 

### Points forts et faiblesses techniques
- **Points forts** :
  - Modularité exemplaire du code backend (FastAPI Dependency Injection bien utilisée).
  - Utilisation systématique de Pydantic pour le typage des réponses.
  - La base de données PostgreSQL est bien exploitée avec la syntaxe moderne de SQLAlchemy 2.0 (utilisation de `select()`).
- **Faiblesses** :
  - Manque cruel de tests (unitaires et intégration).
  - Le frontend a migré vers React Router v7 alors que la règle de développement demandait spécifiquement la version v6 (`react-router-dom: ^7.15.0`).
  - L'implémentation de Gemini dans `services/gemini.py` ne respecte pas strictement les modèles prescrits (utilisation de `gemini-2.5-flash` et `gemma-4-31b-it` au lieu de `gemini-1.5-pro` défini dans les règles de conception).

---

## 2. Alignement avec les Objectifs

### Rappel des objectifs principaux
- Plateforme éducative avec transformation de cours en quiz via IA.
- Respect strict de règles de développement (Python 3.11, PEP 8, FastAPI, React 18+, Zustand).
- Modèles spécifiques pour l'IA (Gemini 1.5 Pro pour le résumé/quiz, Gemini 1.5 Flash pour le chat).
- Règles strictes sur la non-modification de `alembic/env.py`, la gestion des erreurs et l'utilisation des variables d'environnement.

### Évaluation : atteinte des objectifs
- **Architecture & Modèles** : L'architecture demandée est globalement respectée. L'ORM est bien utilisé et les endpoints sont typés. Les flux de données sont fonctionnels.
- **Règles spécifiques LearnQuiz** : Le parsing des cours est séparé de l'appel IA. Le JSON est bien extrait des retours Gemini.

### Écarts identifiés
1. **Modèles d'IA** : L'intégration Gemini actuelle utilise la nouvelle génération (modèles de la série 2.5 et Gemma) au lieu de `gemini-1.5-pro` et `gemini-1.5-flash` dictés par le fichier de règles `learnquiz.md`.
2. **Fonctionnalités manquantes** : Le module du "Tutor IA" (feedback pédagogique interactif lors des erreurs de quiz) n'est pas fully implémenté au niveau du contrôleur (`api/tutor.py`).
3. **Tests** : L'injonction des règles globales ("Toute fonction de service doit avoir au moins un test unitaire") n'est pas du tout respectée.
4. **React Router** : Décalage de version pour React Router (v7 au lieu de v6).

---

## 3. Recommandations & Améliorations

### Suggestions prioritaires (Court terme)
- **Compléter le module Tutor IA** : Finaliser l'implémentation du routeur `tutor.py` pour exploiter la méthode `analyze_answer` disponible dans `gemini.py`.
- **Réaligner les modèles IA** : Mettre à jour `services/gemini.py` pour repointer vers les modèles `gemini-1.5-pro` et `gemini-1.5-flash` selon les règles, ou ajuster les règles si les modèles 2.5 sont un choix assumé pour la production.
- **Downgrade React Router** : Revenir sur la version v6 de `react-router-dom` pour assurer la conformité absolue avec le cahier des charges, ou valider le passage à v7 et mettre le document à jour.

### Améliorations architecturales (Moyen terme)
- **Campagne de Tests** : Implémenter Pytest massivement. 
  - Créer des fixtures pour mocker les réponses de `genai_client` (ne pas consommer de crédits IA durant les tests).
  - Écrire des tests unitaires pour `services/parser.py` et `services/quiz_engine.py`.
  - Ajouter des tests d'intégration sur les endpoints FastAPI.
- **Frontend Tests** : Ajouter Vitest ou Jest ainsi que React Testing Library côté frontend.

### Bonnes pratiques à adopter (Long terme)
- **CI/CD** : Mettre en place un pipeline (ex: GitHub Actions) pour lancer les linters (Ruff/Black/Eslint) et les tests à chaque commit.
- **Observabilité** : Ajouter un système de logs structurés ou APM (ex: Sentry) pour surveiller particulièrement les échecs de parsing de l'IA (JSON malformé).

---

## 4. UI/UX & Expérience Utilisateur

### Évaluation globale du design
- L'utilisation de CSS Modules pour le design assure une bonne étanchéité des styles.
- Les dossiers présents (`AuthLayout`, `CourseChat`, `QuizQuestionView`) montrent une volonté d'offrir une interface modulaire et composable.
- Le projet s'appuie sur des composants spécifiques plutôt que d'importer une lourde bibliothèque UI, ce qui favorise la légèreté.

### Points forts et faiblesses visuels
- **Points forts** : Séparation propre des composants. L'application possède un point d'entrée pour la connexion Google OAuth qui fluidifie l'expérience d'onboarding.
- **Faiblesses** : L'utilisation de CSS pur ou de CSS Modules peut s'avérer chronophage pour maintenir une grande consistance visuelle (design system unifié) au fur et à mesure que le projet grossira. 

### Recommandations d'amélioration
- **Design System / Utility Classes** : Bien que Tailwind CSS soit autorisé en alternative dans les règles (`frontend.md`), le projet a choisi CSS Modules. Il serait bénéfique de définir des variables CSS (custom properties) globales dans `index.css` (couleurs, espacements, typographie) pour maintenir une cohérence.
- **Feedback Asynchrone** : Étant donné que le processing d'un cours (upload -> parsing -> IA génération) peut prendre du temps, s'assurer que `LoadingScreen` soit accompagné d'un skeleton UI ou d'indications précises sur la progression pour rassurer l'utilisateur.
- **Accessibilité (a11y)** : S'assurer que les options de quiz (MCQ) sont gérées sous forme de listes HTML et d'inputs radio sémantiques pour la navigation au clavier et la compatibilité avec les lecteurs d'écran.
