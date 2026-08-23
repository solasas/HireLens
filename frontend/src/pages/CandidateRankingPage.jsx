import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCandidateRanking, getJob } from "../api/jobs";
import { useAsync } from "../hooks/useAsync";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { FitBadge } from "../components/common/FitBadge";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { EmptyState } from "../components/common/EmptyState";
import styles from "./CandidateRankingPage.module.css";

const PAGE_SIZE = 10;

export function CandidateRankingPage() {
  const { jobId } = useParams();
  const [page, setPage] = useState(1);

  const fetchJob = useCallback(() => getJob(jobId), [jobId]);
  const { data: job } = useAsync(fetchJob, [jobId]);

  const fetchRanking = useCallback(
    () => getCandidateRanking(jobId, { page, pageSize: PAGE_SIZE }),
    [jobId, page]
  );
  const { data, error, isLoading, refetch } = useAsync(fetchRanking, [jobId, page]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div>
      <h1>Candidate Ranking</h1>
      {job && <p className={styles.subtitle}>{job.title}</p>}

      {isLoading && <LoadingState label="Loading ranking…" />}
      {!isLoading && error && <ErrorState message={error} onRetry={refetch} />}

      {!isLoading && !error && data && data.candidates.length === 0 && (
        <EmptyState
          title="No candidates evaluated yet"
          description="Upload resumes for this job to see a ranked list here."
          action={
            <Link to={`/jobs/${jobId}/upload`}>
              <Button>Upload resumes</Button>
            </Link>
          }
        />
      )}

      {!isLoading && !error && data && data.candidates.length > 0 && (
        <Card>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate</th>
                  <th>Score</th>
                  <th>Fit level</th>
                </tr>
              </thead>
              <tbody>
                {data.candidates.map((candidate) => (
                  <tr key={candidate.evaluation_id}>
                    <td className={styles.rankCell}>{candidate.rank}</td>
                    <td>
                      <Link to={`/jobs/${jobId}/evaluations/${candidate.evaluation_id}`}>
                        {candidate.name}
                      </Link>
                    </td>
                    <td className={styles.scoreCell}>{candidate.score.toFixed(1)}</td>
                    <td>
                      <FitBadge fitLevel={candidate.fit_level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className={styles.pagination}>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p - 1)}
                disabled={page <= 1}
              >
                Previous
              </Button>
              <span className={styles.pageLabel}>
                Page {page} of {totalPages}
              </span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
