import styles from "./ScoreBar.module.css";

/** value is a 0-1 fraction (the sub-scores from the matching engine). */
export function ScoreBar({ label, value }) {
  const percent = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <div className={styles.row}>
      <div className={styles.labelRow}>
        <span className={styles.label}>{label}</span>
        <span className={styles.percent}>{percent}%</span>
      </div>
      <div
        className={styles.track}
        role="progressbar"
        aria-label={label}
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className={styles.fill} style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
