import { NavLink } from "react-router-dom";
import styles from "./NavBar.module.css";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/jobs", label: "Job Descriptions" },
];

export function NavBar() {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>Smart Resume Screener</div>
      <nav className={styles.nav}>
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
