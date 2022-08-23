import { useEffect, useState } from "react";
import { shouldPolyfill } from "@formatjs/intl-numberformat/should-polyfill";

export const usePolyfillIntlNumberFormat = () => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Polyfill is not supported in Safari < 14 and Edge, import dynamically.
    // This also means that for those browsers we will not support a compact format.
    (async () => {
      if (shouldPolyfill()) {
        await import("@formatjs/intl-numberformat/polyfill");
      }
      if (Intl.NumberFormat.polyfilled) {
        await import("@formatjs/intl-numberformat/locale-data/en");
      }
      setIsReady(true);
    })();
  }, []);

  return isReady;
};
