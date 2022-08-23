import { isEmpty } from "utils/arrays";

export const initialize = (id, sv) => {
  (function (h, o, t, j, a, r) {
    h.hj =
      h.hj ||
      function () {
        (h.hj.q = h.hj.q || []).push(arguments);
      };
    h._hjSettings = { hjid: id, hjsv: sv };
    h._scriptPath = t + h._hjSettings.hjid + j + h._hjSettings.hjsv;
    if (!document.querySelector(`script[src*="${h._scriptPath}"]`)) {
      a = o.getElementsByTagName("head")[0];
      r = o.createElement("script");
      r.async = 1;
      r.src = t + h._hjSettings.hjid + j + h._hjSettings.hjsv;
      a.appendChild(r);
    }
  })(window, document, "https://static.hotjar.com/c/hotjar-", ".js?sv=");
};

// If there is a chance that the code will be run before the Hotjar script has loaded, activate this.
// Not needed for now
// const getHj = () => {
//   return (window.hj =
//     window.hj ||
//     function () {
//       (window.hj.q = window.hj.q || []).push(arguments);
//     });
// };

export const tag = (tags) => {
  const hj = window.hj;
  if (hj && !isEmpty(tags)) {
    hj("tagRecording", tags);
  }
};
