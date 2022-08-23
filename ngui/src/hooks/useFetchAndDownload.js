import { useState } from "react";
import { GET_TOKEN } from "api/auth/actionTypes";
import { useApiData } from "./useApiData";

const getFilenameFromHeader = (header) => header?.match(/filename="(.+)"/)[1];

const getHeaders = (token) => {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Authorization", `Bearer ${token}`);

  return headers;
};

const download = (data, filename, type) => {
  // It is necessary to create a new blob object with mime-type explicitly set for all browsers except Chrome, but it works for Chrome too
  const blob = new Blob([data], { type });

  // Handle MS Edge and IE
  if (window.navigator && window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(blob, filename);
  } else {
    const objUrl = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = objUrl;
    link.download = filename;
    link.click();

    // Firefox requires a delay before revoking the ObjectURL
    setTimeout(() => {
      window.URL.revokeObjectURL(objUrl);
    }, 200);
  }
};

export const useFetchAndDownload = () => {
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  const [isFileDownloading, setIsFileDownloading] = useState(false);

  const fetchAndDownload = ({ url, fallbackFilename, type = null }) => {
    if (isFileDownloading) {
      console.warn("We do not do multiple files loading, please wait while file is fully loaded");
      return;
    }

    setIsFileDownloading(true);

    fetch(url, { method: "GET", headers: getHeaders(token) })
      .then(async (res) => ({
        filename: getFilenameFromHeader(res.headers.get("Content-Disposition")) ?? fallbackFilename,
        blob: await res.blob(),
        type: type || res.headers.get("Content-Type") || "plain/text"
      }))
      .then((res) => {
        download(res.blob, res.filename, res.type);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setIsFileDownloading(false);
      });
  };

  return { isFileDownloading, fetchAndDownload };
};
