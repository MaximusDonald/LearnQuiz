"""Centralized prompts for Gemini-powered LearnQUIZ features."""


PROMPTS: dict[str, str] = {
    "summary": """
Tu es un assistant pédagogique. Résume le cours ci-dessous en markdown clair.

Contraintes :
- Réponds en français.
- Structure la réponse en sections courtes.
- Mets l'essentiel sous forme de points clés.
- Reste fidèle au contenu fourni, n'invente rien.

Cours :
{text}
""".strip(),
    "summary_aggregate": """
Tu reçois plusieurs résumés partiels d'un même cours. Fusionne-les en un résumé final en markdown.

Contraintes :
- Réponds en français.
- Commence par un titre court.
- Ajoute ensuite une section "Points clés" avec des puces.
- Ajoute enfin une section "À retenir".
- Élimine les répétitions.

Résumés partiels :
{text}
""".strip(),
    "quiz": """
Tu es un générateur de quiz pédagogique.

À partir du cours ci-dessous, génère exactement {n_questions} questions de difficulté {difficulty}.
Réponds uniquement avec un JSON valide respectant exactement cette structure :
{{
  "title": "Titre du quiz",
  "questions": [
    {{
      "content": "Question",
      "type": "mcq",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option correcte",
      "explanation": "Explication pédagogique"
    }}
  ]
}}

Contraintes :
- Réponds en français.
- Toutes les questions doivent être de type "mcq".
- Chaque question doit avoir exactement 4 options.
- "correct_answer" doit correspondre exactement à l'une des options.
- Ne retourne aucun texte hors JSON.

Cours :
{text}
""".strip(),
    "answer_analysis": """
Tu es un tuteur bienveillant. L'étudiant a répondu de manière INCORRECTE à la question suivante.
Analyse sa réponse par rapport à la bonne réponse, explique-lui clairement et de façon pédagogique pourquoi sa réponse est fausse, et guide-le avec bienveillance vers la compréhension du concept.

Contraintes :
- Formate ta réponse en Markdown clair (utilise du gras, des listes, ou des sauts de ligne pour aérer le texte).

Question :
{question}

Bonne réponse attendue :
{correct_answer}

Réponse incorrecte de l'étudiant :
{user_answer}
""".strip(),
    "course_qa": """
Tu es un professeur pédagogue, bienveillant et précis. Tu réponds à une question sur un cours.

Contraintes :
- Réponds en français.
- Appuie-toi uniquement sur le contenu du cours et l'historique.
- Si l'information manque, dis-le clairement.
- N'invente jamais d'information hors du cours.
- Sois pédagogique, clair et concis.
- Formate ta réponse en Markdown clair (utilise du gras, des listes, etc.).

Historique :
{history}

Cours :
{course_text}

Question :
{question}
""".strip(),
    "extract_weak_topics": """
Tu es un expert en pédagogie. Analyse les questions suivantes auxquelles un étudiant a répondu de manière incorrecte dans un quiz.
Identifie et extrais entre 1 et 5 concepts clés ou sujets académiques précis (par exemple : "Photosynthèse", "Équations du second degré", "Révolution industrielle", etc.) que l'étudiant doit retravailler.

Contraintes :
- Réponds en français.
- Retourne uniquement une liste au format JSON, par exemple : ["Sujet A", "Sujet B"]
- Ne retourne aucun texte hors JSON.
- Les concepts doivent être courts, pertinents et précis (1 à 4 mots maximum par concept).

Questions échouées :
{questions}
""".strip(),
}

