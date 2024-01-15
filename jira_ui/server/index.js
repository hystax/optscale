import http from "http";
import path from "path";
import express from "express";
import dotevn from "dotenv";
import rateLimitMiddleware from "./middleware/rateLimitMiddleware.js";
import checkJwtParameterForGetPageRoutesMiddleware from "./middleware/checkJwtParameterForGetPageRoutesMiddleware.js";

dotevn.config();

const app = express();

rateLimitMiddleware(app);

checkJwtParameterForGetPageRoutesMiddleware(app);

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
