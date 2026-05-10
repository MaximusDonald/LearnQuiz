# Skill : Intégration Gemini API

## Quand utiliser ce skill
Quand la tâche implique : appeler Gemini, écrire un prompt, gérer les réponses
de l'IA, ou modifier `services/gemini.py`.

## Pattern standard d'appel Gemini
```python
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_something(text: str) -> dict:
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = PROMPTS["my_task"].format(text=text)
    
    try:
        response = await model.generate_content_async(prompt)
        return parse_json_response(response.text)
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(status_code=502, detail="Erreur service IA")
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