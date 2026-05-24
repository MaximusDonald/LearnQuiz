import { NavLink } from 'react-router-dom'

import { useAuthStore } from '../store/useAuthStore'
import styles from './AppHeader.module.css'


export function AppHeader() {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <NavLink className={styles.brand} to="/dashboard">
          LearnQUIZ
        </NavLink>

        <nav className={styles.nav}>
          <NavLink
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
            to="/dashboard"
          >
            Dashboard
          </NavLink>
          <NavLink
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
            to="/courses"
          >
            Cours
          </NavLink>
          <NavLink
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
            to="/quiz"
          >
            Quiz
          </NavLink>
        </nav>

        <div className={styles.userArea}>
          <span className={styles.userName}>{user?.full_name ?? user?.email ?? 'Compte'}</span>
          <button className={styles.logoutButton} type="button" onClick={logout}>
            Déconnexion
          </button>
        </div>
      </div>
    </header>
  )
}
