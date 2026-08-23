import { Card } from "../common/Card";
import { FitBadge } from "../common/FitBadge";
import { ScoreBreakdown } from "../common/ScoreBreakdown";
import { SkillTagList } from "../common/SkillTagList";
import styles from "./EvaluationDetailView.module.css";

/**
 * Renders one evaluation in full: candidate identity, overall score and
 * fit level, the five-component breakdown, matched/missing skills, and
 * the LLM's narrative. Used by both EvaluationResultsPage (right after
 * submitting a batch) and CandidateDetailsPage (from the ranking
 * table) — the content requirement is identical for both, so the view
 * lives once instead of being duplicated per page.
 */
export function EvaluationDetailView({ evaluation }) {
  return (
    <div>
      <Card>
        <div className={styles.headerRow}>
          <div>
            <h1 className={styles.name}>{evaluation.candidate_name}</h1>
            <p className={styles.jobTitle}>for {evaluation.job_title}</p>
          </div>
          <div className={styles.scoreBlock}>
            <span className={styles.score}>{evaluation.score.toFixed(1)}</span>
            <span className={styles.scoreMax}>/ 10</span>
            <FitBadge fitLevel={evaluation.fit_level} />
          </div>
        </div>
      </Card>

      <Card title="Score breakdown">
        <ScoreBreakdown breakdown={evaluation.score_breakdown} />
      </Card>

      <Card title="Matching skills">
        <SkillTagList
          skills={evaluation.matched_skills}
          variant="matched"
          emptyLabel="No required skills matched."
        />
      </Card>

      <Card title="Missing required skills">
        <SkillTagList
          skills={evaluation.missing_required_skills}
          variant="missing"
          emptyLabel="No required skills are missing."
        />
      </Card>

      {evaluation.matched_preferred_skills?.length > 0 && (
        <Card title="Matching preferred skills">
          <SkillTagList skills={evaluation.matched_preferred_skills} variant="neutral" />
        </Card>
      )}

      <Card title="Strengths">
        {evaluation.strengths.length > 0 ? (
          <ul className={styles.list}>
            {evaluation.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className={styles.muted}>No notable strengths identified.</p>
        )}
      </Card>

      <Card title="Relevant experience">
        {evaluation.relevant_experience.length > 0 ? (
          <ul className={styles.list}>
            {evaluation.relevant_experience.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className={styles.muted}>No directly relevant experience identified.</p>
        )}
      </Card>

      <Card title="Concerns">
        {evaluation.concerns.length > 0 ? (
          <ul className={styles.list}>
            {evaluation.concerns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className={styles.muted}>No concerns identified.</p>
        )}
      </Card>

      <Card title="Recommendation">
        <p className={styles.recommendation}>{evaluation.recommendation}</p>
      </Card>
    </div>
  );
}
