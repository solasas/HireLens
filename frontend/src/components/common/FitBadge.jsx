import styles from "./FitBadge.module.css";

const VARIANT_BY_FIT_LEVEL = {
  "Strong Fit": "success",
  "Moderate Fit": "warning",
  "Weak Fit": "danger",
};

export function FitBadge({ fitLevel }) {
  const variant = VARIANT_BY_FIT_LEVEL[fitLevel] || "neutral";
  return <span className={`${styles.badge} ${styles[variant]}`}>{fitLevel}</span>;
}
