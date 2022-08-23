const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = (app) => {
  app.use(
    "/api",
    createProxyMiddleware({
      target: process.env.REACT_APP_PROXY,
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        "^/api": "/"
      }
    })
  );
};
