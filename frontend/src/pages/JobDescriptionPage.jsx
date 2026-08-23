import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createJob, listJobs } from "../api/jobs";
import { getErrorMessage } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { EmptyState } from "../components/common/EmptyState";
import styles from "./JobDescriptionPage.module.css";

const MIN_LENGTH = 1;
const MAX_LENGTH = 20000;

export function JobDescriptionPage() {
  const navigate = useNavigate();
  const { data: jobs, error: listError, isLoading: isListLoading, refetch } = useAsync(
    listJobs,
    []
  );

  const [text, setText] = useState("");
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const trimmedLength = text.trim().length;
  const isValid = trimmedLength >= MIN_LENGTH && text.length <= MAX_LENGTH;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!isValid || isSubmitting) return;

    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const job = await createJob(text);
      navigate(`/jobs/${job.job_id}/upload`);
    } catch (error) {
      setSubmitError(getErrorMessage(error));
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Job Descriptions</h1>

      <Card title="Create a new job description">
        <form onSubmit={handleSubmit}>
          <textarea
            className={styles.textarea}
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Paste the full job description here…"
            rows={10}
            disabled={isSubmitting}
          />
          <div className={styles.formFooter}>
            <span className={styles.charCount}>
              {text.length} / {MAX_LENGTH}
            </span>
            <Button type="submit" disabled={!isValid || isSubmitting}>
              {isSubmitting ? "Analyzing…" : "Create job"}
            </Button>
          </div>
          {submitError && <ErrorState message={submitError} />}
        </form>
      </Card>

      <Card title="Existing jobs">
        {isListLoading && <LoadingState label="Loading jobs…" />}
        {!isListLoading && listError && <ErrorState message={listError} onRetry={refetch} />}
        {!isListLoading && !listError && jobs && jobs.length === 0 && (
          <EmptyState
            title="No jobs yet"
            description="Create your first job description above to start evaluating candidates."
          />
        )}
        {!isListLoading && !listError && jobs && jobs.length > 0 && (
          <ul className={styles.jobList}>
            {jobs.map((job) => (
              <li key={job.job_id} className={styles.jobItem}>
                <div>
                  <span className={styles.jobTitle}>{job.title}</span>
                  <span className={styles.jobMeta}>
                    {job.candidate_count} candidate{job.candidate_count === 1 ? "" : "s"} evaluated
                  </span>
                </div>
                <div className={styles.jobActions}>
                  <Link to={`/jobs/${job.job_id}/upload`}>Upload resumes</Link>
                  <Link to={`/jobs/${job.job_id}/ranking`}>View ranking</Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
