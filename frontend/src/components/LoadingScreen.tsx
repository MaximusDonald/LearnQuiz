import styles from './LoadingScreen.module.css'


interface LoadingScreenProps {
  title?: string
  message?: string
}


export function LoadingScreen({
  title = 'Chargement de ta session',
  message = 'Nous vérifions ton accès avant d’afficher la page.',
}: LoadingScreenProps) {
  return (
    <main className={styles.page}>
      <section className={styles.card}>
        <span className={styles.kicker}>LearnQUIZ</span>
        <h1>{title}</h1>
        <p>{message}</p>
        <svg className={styles.spinner} viewBox="0 0 50 50">
          <circle cx="25" cy="25" r="20" />
        </svg>
      </section>
    </main>
  )
}
