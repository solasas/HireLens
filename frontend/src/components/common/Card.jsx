import styles from "./Card.module.css";

export function Card({ title, children, actions }) {
  return (
    <section className={styles.card}>
      {(title || actions) && (
        <div className={styles.header}>
          {title && <h2>{title}</h2>}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
