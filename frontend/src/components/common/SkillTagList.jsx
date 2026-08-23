import styles from "./SkillTagList.module.css";

/** variant: "matched" | "missing" | "neutral" */
export function SkillTagList({ skills, variant = "neutral", emptyLabel = "None" }) {
  if (!skills || skills.length === 0) {
    return <p className={styles.empty}>{emptyLabel}</p>;
  }
  return (
    <ul className={styles.list}>
      {skills.map((skill) => (
        <li key={skill} className={`${styles.tag} ${styles[variant]}`}>
          {skill}
        </li>
      ))}
    </ul>
  );
}
