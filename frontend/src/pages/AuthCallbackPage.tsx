import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import styles from './ShellPage.module.css'
import { useAuthStore } from '../store/useAuthStore'


export function AuthCallbackPage() {
  const completeSession = useAuthStore((state) => state.completeSession)
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function finalizeGoogleAuth() {
      const params = new URLSearchParams(window.location.search)
      const accessToken = params.get('access_token')
      const refreshToken = params.get('refresh_token')

      if (!accessToken || !refreshToken) {
        setError('Le retour Google ne contient pas les tokens attendus.')
        return
      }

      try {
        await completeSession(accessToken, refreshToken)
        navigate('/dashboard', { replace: true })
      } catch {
        setError('Connexion Google impossible pour le moment.')
      }
    }

    void finalizeGoogleAuth()
  }, [completeSession, navigate])

  return (
    <main className={styles.page}>
      <section className={styles.card}>
        <span className={styles.kicker}>Authentification Google</span>
        <h1>Connexion en cours</h1>
        <p>
          {error ?? 'Nous finalisons ta session et récupérons ton profil LearnQUIZ.'}
        </p>
      </section>
    </main>
  )
}
