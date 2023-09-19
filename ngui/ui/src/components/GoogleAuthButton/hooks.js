import { useCallback, useEffect, useRef, useState } from "react";

const checkIsScriptLoaded = () => !!window?.google?.accounts.oauth2;

const useLoadGsiScript = () => {
  const [scriptLoadedSuccessfully, setScriptLoadedSuccessfully] = useState(checkIsScriptLoaded);

  useEffect(() => {
    if (!checkIsScriptLoaded()) {
      window.onGoogleLibraryLoad = () => setScriptLoadedSuccessfully(true);
    }
    return () => {
      window.onGoogleLibraryLoad = undefined;
    };
  }, []);

  return scriptLoadedSuccessfully;
};

const useGoogleLogin = ({ onSuccess, onError, clientId }) => {
  const scriptLoadedSuccessfully = useLoadGsiScript();

  const clientRef = useRef();

  const onSuccessRef = useRef(onSuccess);
  onSuccessRef.current = onSuccess;

  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;

  useEffect(() => {
    if (!scriptLoadedSuccessfully) return;
    try {
      const client = window?.google?.accounts.oauth2.initCodeClient({
        client_id: clientId,
        scope: "openid profile email",
        callback: (response) => {
          if (response.error) return onErrorRef.current?.(response);

          onSuccessRef.current?.(response);
          return true;
        },
        error_callback: (nonOAuthError) => {
          onErrorRef.current?.(nonOAuthError);
        }
      });

      clientRef.current = client;
    } catch (e) {
      console.error("An error occured during Google Auth initialization:", e);
    }
  }, [clientId, scriptLoadedSuccessfully]);

  const login = useCallback(() => clientRef.current?.requestCode(), []);

  return { login, scriptLoadedSuccessfully };
};

export { useGoogleLogin };
