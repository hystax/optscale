import type { ReactNode } from "react";
import { ApolloClient, ApolloProvider, InMemoryCache, split, HttpLink, from } from "@apollo/client";
import { onError, type ErrorResponse } from "@apollo/client/link/error";
import { RetryLink } from "@apollo/client/link/retry";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";
import { errorVar } from "graphql/reactiveVars";
import { useGetToken } from "hooks/useGetToken";
import { useSignOut } from "hooks/useSignOut";
import { processGraphQLErrorData } from "utils/apollo";
import { getEnvironmentVariable } from "utils/env";

type ApolloClientProviderProps = {
  children: ReactNode;
};

const httpBase = getEnvironmentVariable("VITE_APOLLO_HTTP_BASE");
const wsBase = getEnvironmentVariable("VITE_APOLLO_WS_BASE");

const ApolloClientProvider = ({ children }: ApolloClientProviderProps) => {
  const { token } = useGetToken();

  const signOut = useSignOut();

  const cache = new InMemoryCache();

  const httpLink = new HttpLink({
    uri: (operation) => `${httpBase}/api?op=${operation.operationName}`,
    headers: {
      "x-optscale-token": token,
    },
  });

  const wsLink = new GraphQLWsLink(
    createClient({
      url: `${wsBase}/subscriptions`,
    })
  );

  const retryLink = new RetryLink({
    attempts: { max: 3 },
    delay: { initial: 300, max: 2000, jitter: true },
  });

  const errorLink = onError(({ graphQLErrors, networkError, operation }: ErrorResponse) => {
    if (graphQLErrors) {
      graphQLErrors.forEach((graphQLError) => {
        const { message, path, extensions } = graphQLError;

        console.log(`[GraphQL error]: Message: ${message}, Path: ${path}`);

        if (extensions?.response?.status === 401) {
          signOut();
        }
      });

      const firstError = processGraphQLErrorData(graphQLErrors[0]);

      const suppressAlertForErrorCodes = operation?.getContext()?.suppressAlertForErrorCodes ?? [];
      const shouldSuppressAlert = suppressAlertForErrorCodes?.includes(firstError.errorCode) ?? false;

      if (!shouldSuppressAlert) {
        errorVar(firstError);
      }
    }

    /* Just log network errors for now. 
       We rely on custom error codes that are returned in graphQLErrors. 
       It might be useful to cache networkError errors to display alerts as well. 
    */
    if (networkError) {
      console.error(`[Network error]: ${networkError}`);
    }
  });

  const operationTransportLink = split(
    ({ query }) => {
      const definition = getMainDefinition(query);
      return definition.kind === "OperationDefinition" && definition.operation === "subscription";
    },
    wsLink,
    httpLink
  );

  const link = from([retryLink, errorLink, operationTransportLink]);

  const client = new ApolloClient({
    cache,
    link,
  });

  return <ApolloProvider client={client}>{children}</ApolloProvider>;
};

export default ApolloClientProvider;
