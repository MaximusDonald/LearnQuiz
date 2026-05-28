# Règles spécifiques LearnQUIZ

## Architecture IA
- Service Gemini centralisé : toute interaction avec l'API passe par `services/gemini.py`
- Prompts système stockés dans `services/prompts.py` (pas inline dans le code)
- Toujours gérer le cas où Gemini retourne un JSON malformé (try/except + retry)
- Le modèle gemini-2.5-flash est désormais le standard (ou gemma-4-31b-it) pour les quiz, les résumés et les tâches temps réel.

## Parsing de cours
- Priorité d'extraction : pymupdf pour les PDF (meilleur rendu)
- Toujours nettoyer le texte extrait (supprimer les headers/footers répétitifs)
- Stocker le texte brut ET le texte nettoyé séparément

## Sécurité
- Un utilisateur ne peut accéder qu'à ses propres cours (vérification user_id systématique)
- Les fichiers uploadés sont validés (type MIME + taille max 10MB)
- Les fichiers ne sont pas stockés sur disque en prod (extraction texte immédiate)

## Format des quiz (JSON attendu de Gemini)
{
  "questions": [
    {
      "content": "...",
      "type": "mcq",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "explanation": "..."
    }
  ]
}