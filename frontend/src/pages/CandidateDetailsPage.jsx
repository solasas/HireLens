import { useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import { getEvaluation } from "../api/evaluations";
import { useAsync } from "../hooks/useAsync";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { EvaluationDetailView } from "../components/evaluation/EvaluationDetailView";

export function CandidateDetailsPage() {
  const { jobId, evaluationId } = useParams();

  const fetchEvaluation = useCallback(() => getEvaluation(evaluationId), [evaluationId]);
  const { data, error, isLoading, refetch } = useAsync(fetchEvaluation, [evaluationId]);

  if (isLoading) {
    return <LoadingState label="Loading candidate…" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={refetch} />;
  }

  return (
    <div>
      <Link to={`/jobs/${jobId}/ranking`}>← Back to ranking</Link>
      <div style={{ marginTop: "1rem" }}>
        <EvaluationDetailView evaluation={data} />
      </div>
    </div>
  );
}
