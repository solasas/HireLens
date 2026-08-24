import { Link } from "react-router-dom";
import { getDashboardStats } from "../api/dashboard";
import { useAsync } from "../hooks/useAsync";
import { Card } from "../components/common/Card";
import { StatCard } from "../components/common/StatCard";
import { FitBadge } from "../components/common/FitBadge";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { EmptyState } from "../components/common/EmptyState";
import { Button } from "../components/common/Button";
import styles from "./DashboardPage.module.css";

export function DashboardPage() {
  const { data, error, isLoading, refetch } = useAsync(getDashboardStats, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p className={styles.subtitle}>Score resumes against a job description in three steps.</p>

      <Card>
        <ol className={styles.steps}>
          <li className={styles.step}>
            <span className={styles.stepNumber}>1</span>
            <h3 className={styles.stepTitle}>Add a job description</h3>
            <p className={styles.stepDesc}>
              Paste the role's requirements on the{" "}
              <Link to="/jobs">Job Descriptions</Link> page.
            </p>
          </li>
          <li className={styles.step}>
            <span className={styles.stepNumber}>2</span>
            <h3 className={styles.stepTitle}>Upload resumes</h3>
            <p className={styles.stepDesc}>
              Drop in one or more candidate resumes for that job.
            </p>
          </li>
          <li className={styles.step}>
            <span className={styles.stepNumber}>3</span>
            <h3 className={styles.stepTitle}>Review the scoring</h3>
            <p className={styles.stepDesc}>
              Get an AI-generated fit score, matched/missing skills, and a ranked
              candidate list.
            </p>
          </li>
        </ol>
      </Card>

      {isLoading && <LoadingState label="Loading dashboard…" />}
      {!isLoading && error && <ErrorState message={error} onRetry={refetch} />}

      {!isLoading && !error && data && (
        <>
          <div className={styles.statGrid}>
            <StatCard label="Candidates" value={data.candidate_count} />
            <StatCard
              label="Average score"
              value={data.average_score != null ? data.average_score.toFixed(1) : "—"}
              hint="out of 10"
            />
            <StatCard label="Strong matches" value={data.strong_match_count} />
          </div>

          <Card title="Recent evaluations">
            {data.recent_evaluations.length === 0 ? (
              <EmptyState
                title="No evaluations yet"
                description="Create a job description and evaluate resumes against it to see results here."
                action={
                  <Link to="/jobs">
                    <Button>Create a job description</Button>
                  </Link>
                }
              />
            ) : (
              <ul className={styles.recentList}>
                {data.recent_evaluations.map((evaluation) => (
                  <li key={evaluation.evaluation_id} className={styles.recentItem}>
                    <Link
                      to={`/jobs/${evaluation.job_id}/evaluations/${evaluation.evaluation_id}`}
                      className={styles.recentLink}
                    >
                      <div>
                        <span className={styles.candidateName}>{evaluation.candidate_name}</span>
                        <span className={styles.jobTitle}> — {evaluation.job_title}</span>
                      </div>
                      <div className={styles.recentMeta}>
                        <span className={styles.recentScore}>{evaluation.score.toFixed(1)}</span>
                        <FitBadge fitLevel={evaluation.fit_level} />
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
