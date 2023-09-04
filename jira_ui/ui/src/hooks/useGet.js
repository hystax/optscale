import { useCallback, useEffect, useState } from "react";
import makeRequest from "utils/makeRequest";

export const useGet = (url) => {
  const [apiData, setApiData] = useState(null);
  const [apiLoading, setApiLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  const fetchData = useCallback(() => {
    setApiLoading(true);
    setApiError(null);

    makeRequest({
      url,
      options: {
        method: "GET"
      }
    }).then(({ data, error }) => {
      setApiData(data);
      setApiLoading(false);
      setApiError(error);
    });
  }, [url]);

  useEffect(() => {
    if (url) {
      fetchData();
    }
  }, [fetchData, url]);

  return { loading: apiLoading, error: apiError, data: apiData, refetch: fetchData };
};
