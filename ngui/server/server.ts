import http from "http";
import path from "path";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { ApolloServerPluginDrainHttpServer } from "@apollo/server/plugin/drainHttpServer";
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import { createProxyMiddleware } from "http-proxy-middleware";
import expressRateLimit from "express-rate-limit";
import checkEnvironment from "./checkEnvironment.js";
import KeeperClient from "./api/keeper/client.js";
import SlackerClient from "./api/slacker/client.js";
import RestApiClient from "./api/restapi/client.js";
import AuthClient from "./api/auth/client.js";
import { schema } from "./graphql/schema.js";

if (process.env.NODE_ENV === "development") {
  const dotenv = await import("dotenv");
  const dotenvExpand = await import("dotenv-expand");
  const myEnv = dotenv.config();
  dotenvExpand.expand(myEnv);
}

checkEnvironment(["UI_BUILD_PATH", "PROXY_URL"]);

const app = express();

// https://github.com/express-rate-limit/express-rate-limit/wiki/Troubleshooting-Proxy-Issues
app.set("trust proxy", 1);

const httpServer = http.createServer(app);

export interface ContextValue {
  dataSources: {
    keeper: KeeperClient;
    slacker: SlackerClient;
    restapi: RestApiClient;
    auth: AuthClient;
  };
}

const server = new ApolloServer<ContextValue>({
  schema,
  plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
});

// Ensure we wait for our server to start
await server.start();

// Set up our Express middleware to handle CORS, body parsing,
// and our expressMiddleware function.
app.use(
  "/api",
  cors<cors.CorsRequest>(),
  bodyParser.json(),
  // expressMiddleware accepts the same arguments:
  // an Apollo Server instance and optional configuration options
  expressMiddleware(server, {
    context: async ({ req }) => {
      const { cache } = server;

      const token = req.headers["x-optscale-token"] as string;

      return {
        // We create new instances of our data sources with each request,
        // passing in our server's cache.
        dataSources: {
          keeper: new KeeperClient({ cache }, token, "http://keeper"),
          slacker: new SlackerClient({ cache }, token, "http://slacker"),
          restapi: new RestApiClient({ cache }, token, "http://restapi"),
          auth: new AuthClient({ cache }, token, "http://auth"),
        },
      };
    },
  })
);

// Temporary proxy until we migrate the APIs.
const proxyMiddleware = createProxyMiddleware({
  target: process.env.PROXY_URL,
  changeOrigin: true,
  secure: false,
});

app.use("/auth", proxyMiddleware);
app.use("/jira_bus", proxyMiddleware);
app.use("/restapi", proxyMiddleware);

const UI_BUILD_PATH = process.env.UI_BUILD_PATH;
const UI_BUILD_DIR = (process.env.UI_BUILD_DIR || "build").trim();

// Validate UI_BUILD_DIR to prevent path traversal and absolute paths
if (UI_BUILD_DIR.includes("..") || UI_BUILD_DIR.startsWith("/")) {
  throw new Error("Invalid UI_BUILD_DIR: path traversal and absolute paths are not allowed");
}

const staticDir = path.join(UI_BUILD_PATH, UI_BUILD_DIR);

app.use(express.static(staticDir, { index: false }));

const indexLimiter = expressRateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 500,
});

app.get("*", indexLimiter, (_, res) => res.sendFile(path.join(staticDir, "index.html")));

const port = parseInt(process.env.PORT || "4000", 10);

await new Promise<void>((resolve) => httpServer.listen({ port }, resolve));

console.log(`🚀 Server ready at http://localhost:${port}/`);
