import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import styles from './AuthLayout.module.css'


interface AuthLayoutProps {
  title: string
  subtitle: string
  alternateLabel: string
  alternateHref: string
  alternateCta: string
  children: ReactNode
}


export function AuthLayout({
  title,
  subtitle,
  alternateLabel,
  alternateHref,
  alternateCta,
  children,
}: AuthLayoutProps) {
  return (
    <main className={styles.page}>
      <section className={styles.heroPanel}>
        <div className={styles.heroBadge}>LearnQUIZ</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <div className={styles.heroGrid}>
          <article>
            <span>Quiz IA</span>
            <strong>Génération instantanée depuis tes cours.</strong>
          </article>
          <article>
            <span>Suivi</span>
            <strong>Repère tes points faibles et revois l’essentiel.</strong>
          </article>
        </div>
      </section>

      <section className={styles.formPanel}>
        <div className={styles.formCard}>
          {children}
          <p className={styles.footerText}>
            {alternateLabel}{' '}
            <Link to={alternateHref}>{alternateCta}</Link>
          </p>
        </div>
      </section>
    </main>
  )
}
