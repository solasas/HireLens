import { useCallback, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { evaluateCandidates, getJob } from "../api/jobs";
import { getErrorMessage } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { LoadingState } from "../components/common/LoadingState";
import { ErrorState } from "../components/common/ErrorState";
import { FileDropzone } from "../components/upload/FileDropzone";

export function UploadResumePage() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const fetchJob = useCallback(() => getJob(jobId), [jobId]);
  const { data: job, error: jobError, isLoading: isJobLoading, refetch } = useAsync(fetchJob, [
    jobId,
  ]);

  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleEvaluate = async () => {
    if (files.length === 0 || isSubmitting) return;

    setIsSubmitting(true);
    setSubmitError(null);
    setUploadProgress(0);
    try {
      const result = await evaluateCandidates(jobId, files, (event) => {
        if (event.total) {
          setUploadProgress(Math.round((event.loaded / event.total) * 100));
        }
      });
      navigate(`/jobs/${jobId}/results`, {
        state: { evaluationIds: result.evaluation_ids },
      });
    } catch (error) {
      setSubmitError(getErrorMessage(error));
      setIsSubmitting(false);
      setUploadProgress(null);
    }
  };

  if (isJobLoading) {
    return <LoadingState label="Loading job…" />;
  }

  if (jobError) {
    return <ErrorState message={jobError} onRetry={refetch} />;
  }

  return (
    <div>
      <h1>Upload Resumes</h1>
      <p>
        Evaluating candidates for <strong>{job.title}</strong>.
      </p>

      <Card title="Resume files">
        <FileDropzone
          files={files}
          onFilesChange={setFiles}
          uploadProgress={uploadProgress}
          disabled={isSubmitting}
        />

        {submitError && <ErrorState message={submitError} />}

        <div style={{ marginTop: "1rem" }}>
          <Button onClick={handleEvaluate} disabled={files.length === 0 || isSubmitting}>
            {isSubmitting
              ? "Evaluating…"
              : `Evaluate ${files.length || ""} candidate${files.length === 1 ? "" : "s"}`}
          </Button>
        </div>
      </Card>
    </div>
  );
}
