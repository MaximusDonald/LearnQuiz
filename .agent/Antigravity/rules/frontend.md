# Règles Frontend

## Stack
- React 18+ avec TypeScript (strict mode)
- Vite comme bundler
- Zustand pour l'état global
- Axios pour les appels API
- React Router v6 pour le routing

## Style
- Composants fonctionnels uniquement (pas de classes)
- Named exports préférés aux default exports
- Props typées avec interface TypeScript
- CSS Modules ou Tailwind CSS (pas de styles inline)

## Conventions
- Un composant = un fichier
- Nommage PascalCase pour les composants
- Nommage camelCase pour les hooks, fonctions, variables
- Les hooks custom commencent par "use" (ex: useAuth, useCourses)

## Performance
- Mémoïser avec useMemo/useCallback quand pertinent
- Lazy loading pour les pages avec React.lazy
- Éviter les re-renders inutiles