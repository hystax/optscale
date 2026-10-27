import type { GraphQLFormattedError } from "graphql";
import { v4 as uuidv4 } from "uuid";

export const processGraphQLErrorData = (graphQLError: GraphQLFormattedError) => {
  const { extensions: { response: { url, body: { error } = {} } = {} } = {}, message } = graphQLError;

  return {
    id: uuidv4(),
    url,
    errorCode: error?.error_code,
    errorReason: error?.reason,
    params: error?.params,
    apolloErrorMessage: message,
  };
};
