import { ApolloClient, ApolloProvider, InMemoryCache, split, HttpLink } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";
import { GET_TOKEN } from "api/auth/actionTypes";
import { useApiData } from "hooks/useApiData";
import { getEnvironmentVariable } from "utils/env";

const httpBase = getEnvironmentVariable("VITE_APOLLO_HTTP_BASE");
const wsBase = getEnvironmentVariable("VITE_APOLLO_WS_BASE");

const ApolloClientProvider = ({ children }) => {
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  const httpLink = new HttpLink({
    uri: `${httpBase}/api`,
    headers: {
      "x-optscale-token": token
    }
  });

  const wsLink = new GraphQLWsLink(
    createClient({
      url: `${wsBase}/subscriptions`
    })
  );

  /* 
   @param A function that's called for each operation to execute
   @param The Link to use for an operation if the function returns a "truthy" value
   @param The Link to use for an operation if the function returns a "falsy" value
  */
  const splitLink = split(
    ({ query }) => {
      const definition = getMainDefinition(query);
      return definition.kind === "OperationDefinition" && definition.operation === "subscription";
    },
    wsLink,
    httpLink
  );

  const client = new ApolloClient({
    link: splitLink,
    cache: new InMemoryCache()
  });

  return <ApolloProvider client={client}>{children}</ApolloProvider>;
};

export default ApolloClientProvider;
