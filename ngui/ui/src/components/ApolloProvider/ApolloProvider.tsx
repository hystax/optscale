import { ApolloClient, ApolloProvider, InMemoryCache, split, HttpLink, from, type DefaultContext } from "@apollo/client";
import { onError, type ErrorResponse } from "@apollo/client/link/error";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { type GraphQLError } from "graphql";
import { createClient } from "graphql-ws";
import { GET_TOKEN } from "api/auth/actionTypes";
import { GET_ERROR } from "graphql/api/common";
import { useApiData } from "hooks/useApiData";
import { getEnvironmentVariable } from "utils/env";

const httpBase = getEnvironmentVariable("VITE_APOLLO_HTTP_BASE");
const wsBase = getEnvironmentVariable("VITE_APOLLO_WS_BASE");

const writeErrorToCache = (cache: DefaultContext, graphQLError: GraphQLError) => {
  const { extensions: { response: { url, body: { error } = {} } = {} } = {} } = graphQLError;

  cache.writeQuery({
    query: GET_ERROR,
    data: { error: { __typename: "Error", ...error, url } }
  });
};

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

  const errorLink = onError(({ graphQLErrors, networkError, operation }: ErrorResponse) => {
    if (graphQLErrors) {
      graphQLErrors.forEach(({ message, path }) => console.log(`[GraphQL error]: Message: ${message}, Path: ${path}`));

      const { cache } = operation.getContext();
      writeErrorToCache(cache, graphQLErrors[0]);
    }

    /* Just log network errors for now. 
       We rely on custom error codes that are returned in graphQLErrors. 
       It might be usefult to cache networkError errors to display alerts as well. 
    */
    if (networkError) {
      console.error(`[Network error]: ${networkError}`);
    }
  });

  const splitLink = split(
    ({ query }) => {
      const definition = getMainDefinition(query);
      return definition.kind === "OperationDefinition" && definition.operation === "subscription";
    },
    wsLink,
    httpLink
  );

  const client = new ApolloClient({
    link: from([errorLink, splitLink]),
    cache: new InMemoryCache()
  });

  return <ApolloProvider client={client}>{children}</ApolloProvider>;
};

export default ApolloClientProvider;
