import { Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { JobDescriptionPage } from "./pages/JobDescriptionPage";
import { UploadResumePage } from "./pages/UploadResumePage";
import { EvaluationResultsPage } from "./pages/EvaluationResultsPage";
import { CandidateRankingPage } from "./pages/CandidateRankingPage";
import { CandidateDetailsPage } from "./pages/CandidateDetailsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/**
 * Routing shell only — every page's actual logic lives in src/pages/
 * and every reusable piece of UI lives in src/components/. Nothing is
 * implemented inline here.
 */
export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/jobs" element={<JobDescriptionPage />} />
        <Route path="/jobs/:jobId/upload" element={<UploadResumePage />} />
        <Route path="/jobs/:jobId/results" element={<EvaluationResultsPage />} />
        <Route path="/jobs/:jobId/ranking" element={<CandidateRankingPage />} />
        <Route path="/jobs/:jobId/evaluations/:evaluationId" element={<CandidateDetailsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
