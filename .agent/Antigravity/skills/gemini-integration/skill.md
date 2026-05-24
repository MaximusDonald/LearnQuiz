# Skill : Intégration Gemini API

## Quand utiliser ce skill
Quand la tâche implique : appeler Gemini, écrire un prompt, gérer les réponses
de l'IA, ou modifier `services/gemini.py`.

## Pattern standard d'appel Gemini
```python
from google import genai
from google.genai import types

from fastapi import HTTPException
from app.core.config import settings

import json
import re
import logging

logger = logging.getLogger(__name__)

# Initialisation du client
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def parse_json_response(text: str) -> dict:
    """
    Nettoie et parse une réponse JSON générée par Gemini
    """
    clean = re.sub(r"```json|```", "", text).strip()
    return json.loads(clean)


PROMPTS = {
    "my_task": """
    Analyse le texte suivant et retourne uniquement un JSON valide.

    Texte :
    {text}
    """
}


async def generate_something(text: str) -> dict:
    prompt = PROMPTS["my_task"].format(text=text)

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        return parse_json_response(response.text)

    except Exception as e:
        logger.error(f"Gemini error: {e}")

        raise HTTPException(
            status_code=502,
            detail="Erreur service IA"
        )
```

## Gestion du JSON malformé
Toujours utiliser cette fonction pour parser les réponses :
```python
import json, re

def parse_json_response(text: str) -> dict:
    # Nettoyer les balises markdown éventuelles
    clean = re.sub(r"```json|```", "", text).strip()
    return json.loads(clean)
```