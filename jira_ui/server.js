const fs = require("fs");
const https = require("https");
const path = require("path");
const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();

const { target, secure } = require("./config")();

const CERT_PATH = "/home/gitlab-runner/certificates";
const BUILD_PATH = path.join(__dirname, "build");
const BUILD_INDEX_PATH = path.join(__dirname, "build", "index.html");

const JIRA_UI_APP_URL_BASE = "/jira_ui";

app.use(
  "/jira_bus",
  createProxyMiddleware({
    target,
    changeOrigin: true,
    secure: false
  })
);

app.use(JIRA_UI_APP_URL_BASE, express.static(BUILD_PATH));

app.use(JIRA_UI_APP_URL_BASE, (req, res) => {
  res.sendFile(BUILD_INDEX_PATH);
});

const PORT = 80;

if (secure) {
  https
    .createServer(
      {
        key: fs.readFileSync(`${CERT_PATH}/staging-selfsigned.key`),
        cert: fs.readFileSync(`${CERT_PATH}/staging-selfsigned.crt`)
      },
      app
    )
    .listen(PORT);
} else {
  app.listen(PORT);
}
