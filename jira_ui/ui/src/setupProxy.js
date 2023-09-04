const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = (app) => {
  app.use(
    "/jira_bus",
    createProxyMiddleware({
      target: `${process.env.REACT_APP_PROXY}`,
      changeOrigin: true,
      secure: false
    })
  );
};
