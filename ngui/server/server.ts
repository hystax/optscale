import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { ApolloServerPluginDrainHttpServer } from "@apollo/server/plugin/drainHttpServer";
import express from "express";
import http from "http";
import cors from "cors";
import path from "path";
import bodyParser from "body-parser";
import dotevn from "dotenv";
import { createProxyMiddleware } from "http-proxy-middleware";
import checkEnvironment from "./checkEnvironment.js";

// Load environemtn variables from .env file
dotevn.config();
checkEnvironment(["UI_BUILD_PATH", "PROXY_URL"]);

// A schema is a collection of type definitions (hence "typeDefs")
// that together define the "shape" of queries that are executed against
// your data.
const typeDefs = `#graphql
  # Comments in GraphQL strings (such as this one) start with the hash (#) symbol.

  # This "Hello" type defines the queryable fields for every hello in our data source.
  type Hello {
    message: String
  }

  # The "Query" type is special: it lists all of the available queries that
  # clients can execute, along with the return type for each. In this
  # case, the "hellos" query returns an array of zero or more Hellos (defined above).
  type Query {
    hellos: [Hello]
  }
`;

const hellos = [
  {
    message: "world",
  },
  {
    title: "test",
  },
];

// Resolvers define the technique for fetching the types defined in the
// schema. This resolver retrieves hellos from the "hellos" array above.
const resolvers = {
  Query: {
    hellos: () => hellos,
  },
};

interface MyContext {
  token?: string;
}

// Required logic for integrating with Express
const app = express();
// Our httpServer handles incoming requests to our Express app.
// Below, we tell Apollo Server to "drain" this httpServer,
// enabling our servers to shut down gracefully.
const httpServer = http.createServer(app);

// Same ApolloServer initialization as before, plus the drain plugin
// for our httpServer.
const server = new ApolloServer<MyContext>({
  typeDefs,
  resolvers,
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
    context: async ({ req }) => ({ token: req.headers.token }),
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
app.use("/keeper", proxyMiddleware);
app.use("/restapi", proxyMiddleware);
app.use("/slacker", proxyMiddleware);

const UI_BUILD_PATH = process.env.UI_BUILD_PATH;

// Serve static build
app.use(express.static(path.join(UI_BUILD_PATH, "build")));

app.get("/*", function (req, res) {
  res.sendFile(path.join(UI_BUILD_PATH, "build", "index.html"));
});

// Modified server startup
await new Promise<void>((resolve) =>
  httpServer.listen({ port: 4000 }, resolve)
);
console.log(`🚀 Server ready at http://localhost:4000/`);
