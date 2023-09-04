const http = require("http");
const path = require("path");
const express = require("express");
const dotevn = require("dotenv");

dotevn.config();

const app = express();

app.use(
  "/jira_ui",
  express.static(path.join(process.env.UI_BUILD_PATH, "build"))
);

app.get("/*", (req, res) => {
  res.sendFile(path.join(process.env.UI_BUILD_PATH, "build", "index.html"));
});

const PORT = 4000;

const httpServer = http.createServer(app);

httpServer.listen({ port: PORT }, () => {
  console.log(`🚀 Server ready at http://localhost:${PORT}/`);
});
