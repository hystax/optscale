const http = require("http");
const path = require("path");
const express = require("express");
const dotevn = require("dotenv");
const { rateLimit } = require("express-rate-limit");

dotevn.config();

const app = express();

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 500, // Limit each IP to 500 requests per `window` (here, per 15 minutes)
});

app.use(limiter);

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
