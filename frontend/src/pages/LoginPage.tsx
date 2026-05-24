import { AxiosError } from 'axios'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom' // Note: 'react-router-dom' dans ton code initial

import { AuthLayout } from '../components/AuthLayout'
import styles from '../components/AuthForm.module.css'
import { useAuthStore } from '../store/useAuthStore'

export function LoginPage() {
  const login = useAuthStore((state) => state.login)
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false) // <-- Nouvel état pour la visibilité
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const redirectTo = (location.state as { from?: string } | null)?.from ?? '/dashboard'
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await login(email, password)
      navigate(redirectTo, { replace: true })
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(axiosError.response?.data?.detail ?? 'Connexion impossible pour le moment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Reprends ton apprentissage là où tu l’as laissé."
      subtitle="Connecte-toi pour retrouver tes cours, tes quiz et ton suivi pédagogique généré par l’IA."
      alternateLabel="Pas encore de compte ?"
      alternateHref="/register"
      alternateCta="Créer un compte"
    >
      <div className={styles.heading}>
        <span className={styles.eyebrow}>Connexion</span>
        <h2 className={styles.title}>Bienvenue</h2>
        <p className={styles.description}>
          Utilise ton email ou connecte-toi avec Google pour accéder à LearnQUIZ.
        </p>
      </div>

      <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
        <label className={styles.field}>
          <span className={styles.label}>Adresse email</span>
          <input
            className={styles.input}
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="toi@example.com"
            autoComplete="email"
            required
          />
        </label>

        <label className={styles.field}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className={styles.label}>Mot de passe</span>
            {/* Bouton pour afficher/masquer */}
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.85rem',
                color: 'var(--primary-color, #007bff)',
                padding: 0
              }}
            >
              {showPassword ? 'Masquer' : 'Afficher'}
            </button>
          </div>
          <input
            className={styles.input}
            type={showPassword ? 'text' : 'password'} // <-- Type dynamique
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Ton mot de passe"
            autoComplete="current-password"
            required
          />
        </label>

        {error ? <div className={styles.error}>{error}</div> : null}

        <button className={styles.submitButton} type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Connexion en cours...' : 'Se connecter'}
        </button>

        <div className={styles.divider}>ou</div>

        <a className={styles.googleButton} href={`${apiBaseUrl}/api/auth/google`}>
          Continuer avec Google
        </a>

        <p className={styles.description}>
          Nouveau sur la plateforme ? <Link to="/register">Créer un compte</Link>
        </p>
      </form>
    </AuthLayout>
  )
}