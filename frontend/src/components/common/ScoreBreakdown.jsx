import { ScoreBar } from "./ScoreBar";
import styles from "./ScoreBreakdown.module.css";

const ROWS = [
  { key: "skill_score", label: "Skills" },
  { key: "experience_score", label: "Experience" },
  { key: "education_score", label: "Education" },
  { key: "semantic_score", label: "Semantic similarity" },
  { key: "project_score", label: "Project relevance" },
];

export function ScoreBreakdown({ breakdown }) {
  return (
    <div className={styles.grid}>
      {ROWS.map((row) => (
        <ScoreBar key={row.key} label={row.label} value={breakdown[row.key] ?? 0} />
      ))}
    </div>
  );
}
