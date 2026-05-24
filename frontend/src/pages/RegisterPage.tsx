import { AxiosError } from 'axios'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { AuthLayout } from '../components/AuthLayout'
import styles from '../components/AuthForm.module.css'
import { registerRequest } from '../services/authApi'
import { useAuthStore } from '../store/useAuthStore'


export function RegisterPage() {
  const completeSession = useAuthStore((state) => state.completeSession)
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false) 
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const response = await registerRequest({
        email,
        password,
        full_name: fullName,
      })
      await completeSession(response.access_token, response.refresh_token, response.user)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(axiosError.response?.data?.detail ?? 'Inscription impossible pour le moment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Transforme tes cours en sessions d’étude guidées."
      subtitle="Crée ton compte pour importer tes supports, générer des quiz et suivre ta progression."
      alternateLabel="Tu as déjà un compte ?"
      alternateHref="/login"
      alternateCta="Se connecter"
    >
      <div className={styles.heading}>
        <span className={styles.eyebrow}>Inscription</span>
        <h2 className={styles.title}>Créer un compte</h2>
        <p className={styles.description}>
          Quelques informations suffisent pour démarrer ton espace LearnQUIZ.
        </p>
      </div>

      <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
        <label className={styles.field}>
          <span className={styles.label}>Nom complet</span>
          <input
            className={styles.input}
            type="text"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            placeholder="Ada Lovelace"
            autoComplete="name"
          />
        </label>

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
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Minimum 8 caractères"
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>

        {error ? <div className={styles.error}>{error}</div> : null}

        <button className={styles.submitButton} type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Création en cours...' : 'Créer mon compte'}
        </button>
      </form>
    </AuthLayout>
  )
}
