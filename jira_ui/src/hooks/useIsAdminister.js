import { useState, useEffect } from "react";

export const useIsAdminister = () => {
  const [apiLoading, setApiLoading] = useState(false);
  const [apiData, setApiData] = useState(null);
  const [apiError, setApiError] = useState(null);

  useEffect(() => {
    setApiLoading(true);
    window.AP.request("/rest/api/3/mypermissions?permissions=ADMINISTER")
      .then(({ body }) => {
        const data = JSON.parse(body);

        setApiData({
          isAdministrator: data.permissions.ADMINISTER.havePermission
        });
        setApiError(null);
      })
      .catch(({ err }) => {
        const error = JSON.parse(err);
        console.error("/rest/api/3/mypermissions", error.errorMessages);

        setApiData(null);
        setApiError(error);
      })
      .finally(() => {
        setApiLoading(false);
      });
  }, []);

  return {
    loading: apiLoading,
    error: apiError,
    data: apiData
  };
};
