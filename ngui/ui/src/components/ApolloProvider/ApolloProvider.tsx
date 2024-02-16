import { ApolloClient, ApolloProvider, InMemoryCache, split, HttpLink } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";
import { GET_TOKEN } from "api/auth/actionTypes";
import { useApiData } from "hooks/useApiData";

const ApolloClientProvider = ({ children }) => {
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  const httpLink = new HttpLink({
    uri: "http://localhost:4000/api",
    headers: {
      "x-optscale-token": token
    }
  });

  const wsLink = new GraphQLWsLink(
    createClient({
      url: "ws://localhost:4000/subscriptions"
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
