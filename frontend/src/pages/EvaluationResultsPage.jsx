import { useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { getEvaluation } from "../api/evaluations";
import { useAsync } from "../hooks/useAsync";
import { Card } from "../components/common/Card";
import { FitBadge } from "../components/common/FitBadge";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { EmptyState } from "../components/common/EmptyState";
import { Button } from "../components/common/Button";
import styles from "./EvaluationResultsPage.module.css";

export function EvaluationResultsPage() {
  const { jobId } = useParams();
  const location = useLocation();
  const evaluationIds = location.state?.evaluationIds ?? [];

  const fetchAll = useCallback(
    () => Promise.all(evaluationIds.map((id) => getEvaluation(id))),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [evaluationIds.join(",")]
  );

  const { data: evaluations, error, isLoading, refetch } = useAsync(fetchAll, [
    evaluationIds.join(","),
  ]);

  if (evaluationIds.length === 0) {
    return (
      <EmptyState
        title="No results to show"
        description="This page shows the candidates you just evaluated. Upload resumes to see results here."
        action={
          <Link to={`/jobs/${jobId}/ranking`}>
            <Button>View full ranking instead</Button>
          </Link>
        }
      />
    );
  }

  return (
    <div>
      <h1>Evaluation Results</h1>

      {isLoading && <LoadingState label="Loading evaluations…" />}
      {!isLoading && error && <ErrorState message={error} onRetry={refetch} />}

      {!isLoading && !error && evaluations && (
        <Card>
          <ul className={styles.list}>
            {evaluations.map((evaluation) => (
              <li key={evaluation.evaluation_id} className={styles.item}>
                <Link
                  to={`/jobs/${jobId}/evaluations/${evaluation.evaluation_id}`}
                  className={styles.link}
                >
                  <span className={styles.name}>{evaluation.candidate_name}</span>
                  <span className={styles.meta}>
                    <span className={styles.score}>{evaluation.score.toFixed(1)}</span>
                    <FitBadge fitLevel={evaluation.fit_level} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Link to={`/jobs/${jobId}/ranking`}>View full candidate ranking →</Link>
    </div>
  );
}
