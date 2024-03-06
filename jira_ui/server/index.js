import http from "http";
import path from "path";
import express from "express";
import dotevn from "dotenv";
import rateLimitMiddleware from "./middleware/rateLimitMiddleware.js";
import checkJwtForPageRoutesMiddleware from "./middleware/checkJwtForPageRoutesMiddleware.js";

dotevn.config();

const app = express();

// https://github.com/express-rate-limit/express-rate-limit/wiki/Troubleshooting-Proxy-Issues
app.set("trust proxy", 1);

rateLimitMiddleware(app);

checkJwtForPageRoutesMiddleware(app);

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
