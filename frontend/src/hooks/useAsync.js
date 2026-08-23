import { useCallback, useEffect, useRef, useState } from "react";
import { getErrorMessage } from "../api/client";

/**
 * Runs an async function on mount (and whenever `deps` changes),
 * exposing { data, error, isLoading, refetch }. Every page's
 * loading/error state comes from this one hook instead of each page
 * re-implementing the same three useState calls.
 *
 * Guards against setting state after unmount (e.g. a slow request
 * outliving a fast page navigation) with a ref-based cancellation flag.
 */
export function useAsync(asyncFn, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const cancelledRef = useRef(false);

  const run = useCallback(() => {
    cancelledRef.current = false;
    setIsLoading(true);
    setError(null);
    asyncFn()
      .then((result) => {
        if (!cancelledRef.current) {
          setData(result);
        }
      })
      .catch((err) => {
        if (!cancelledRef.current) {
          setError(getErrorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelledRef.current) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelledRef.current = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { data, error, isLoading, refetch: run };
}
