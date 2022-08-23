const STAGING_URL = "https://staging.optscale.com/";

module.exports = () => {
  switch (process.env.REACT_APP_ENV) {
    case "staging":
      return {
        target: STAGING_URL,
        secure: true
      };
    case "docker":
      return {
        target: "https://ngingress-nginx-ingress-controller:443"
      };
    default:
      return {
        target: STAGING_URL
      };
  }
};
