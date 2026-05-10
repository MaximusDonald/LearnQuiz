# Règles Python

## Style
- Python 3.11+
- Suivre PEP 8 (max 88 caractères par ligne, formatter Black)
- Type hints obligatoires sur toutes les fonctions
- Préférer async/await pour toutes les opérations I/O

## FastAPI
- Utiliser des routers séparés par domaine fonctionnel
- Les schémas Pydantic pour toutes les entrées/sorties
- HTTPException avec des messages clairs pour les erreurs
- Dépendances FastAPI (Depends) pour l'auth et la DB

## Base de données
- SQLAlchemy 2.0 avec syntaxe moderne (select(), pas query())
- Toujours fermer les sessions DB (utiliser async with)
- Migrations via Alembic uniquement, jamais de create_all() en prod

## Structure des imports
- Standard library → third-party → local (séparés par une ligne vide)