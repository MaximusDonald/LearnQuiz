# Règles globales de développement

## Langue
- Réponds toujours en français dans les explications
- Les commentaires dans le code peuvent être en anglais (convention universelle)
- Les messages de commit git sont en anglais

## Comportement de l'agent
- Avant toute modification de fichier existant, résume ce que tu vas faire
- Ne supprime jamais de code sans confirmation explicite
- Pour chaque tâche complexe, génère d'abord un plan (artifact) avant d'écrire du code
- Si une décision architecturale a plusieurs options, présente-les avec leurs compromis
- Après chaque phase, génère un résumé de ce qui a été fait

## Qualité du code
- Toujours écrire des types explicites (pas de `any` en TypeScript, type hints en Python)
- Chaque fonction doit avoir une docstring ou un commentaire d'en-tête
- Pas de code mort ni de console.log laissés en production
- Les variables d'environnement ne sont jamais hardcodées

## Tests
- Toute fonction de service doit avoir au moins un test unitaire
- Les endpoints FastAPI doivent avoir des tests d'intégration avec pytest
- Utiliser des fixtures pour les données de test

## Sécurité
- Ne jamais afficher de clé API dans les logs ou les réponses
- Valider toutes les entrées utilisateur côté backend
- Paramétrer les requêtes SQL (jamais de concaténation de strings)

## Git
- Commits atomiques : une fonctionnalité = un commit
- Format : type(scope): message  (ex: feat(auth): add google oauth)