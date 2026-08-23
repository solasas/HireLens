import { Link } from "react-router-dom";
import { EmptyState } from "../components/common/EmptyState";
import { Button } from "../components/common/Button";

export function NotFoundPage() {
  return (
    <EmptyState
      title="Page not found"
      description="The page you're looking for doesn't exist."
      action={
        <Link to="/">
          <Button>Back to dashboard</Button>
        </Link>
      }
    />
  );
}
