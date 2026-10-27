import { gql } from "@apollo/client";
import * as Apollo from "@apollo/client";
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
};

export type Mutation = {
  __typename?: "Mutation";
  _empty?: Maybe<Scalars["String"]["output"]>;
  connect?: Maybe<SlackUser>;
};

export type MutationConnectArgs = {
  secret: Scalars["String"]["input"];
};

export type Query = {
  __typename?: "Query";
  _empty?: Maybe<Scalars["String"]["output"]>;
  url?: Maybe<Scalars["String"]["output"]>;
};

export type SlackUser = {
  __typename?: "SlackUser";
  slack_user_id: Scalars["String"]["output"];
};

export type GetInstallationPathQueryVariables = Exact<{ [key: string]: never }>;

export type GetInstallationPathQuery = { __typename?: "Query"; url?: string | null };

export type ConnectSlackUserMutationVariables = Exact<{
  secret: Scalars["String"]["input"];
}>;

export type ConnectSlackUserMutation = {
  __typename?: "Mutation";
  connect?: { __typename?: "SlackUser"; slack_user_id: string } | null;
};

export const GetInstallationPathDocument = gql`
  query GetInstallationPath {
    url
  }
`;

/**
 * __useGetInstallationPathQuery__
 *
 * To run a query within a React component, call `useGetInstallationPathQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetInstallationPathQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetInstallationPathQuery({
 *   variables: {
 *   },
 * });
 */
export function useGetInstallationPathQuery(
  baseOptions?: Apollo.QueryHookOptions<GetInstallationPathQuery, GetInstallationPathQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetInstallationPathQuery, GetInstallationPathQueryVariables>(GetInstallationPathDocument, options);
}
export function useGetInstallationPathLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetInstallationPathQuery, GetInstallationPathQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetInstallationPathQuery, GetInstallationPathQueryVariables>(GetInstallationPathDocument, options);
}
// @ts-ignore
export function useGetInstallationPathSuspenseQuery(
  baseOptions?: Apollo.SuspenseQueryHookOptions<GetInstallationPathQuery, GetInstallationPathQueryVariables>
): Apollo.UseSuspenseQueryResult<GetInstallationPathQuery, GetInstallationPathQueryVariables>;
export function useGetInstallationPathSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetInstallationPathQuery, GetInstallationPathQueryVariables>
): Apollo.UseSuspenseQueryResult<GetInstallationPathQuery | undefined, GetInstallationPathQueryVariables>;
export function useGetInstallationPathSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetInstallationPathQuery, GetInstallationPathQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetInstallationPathQuery, GetInstallationPathQueryVariables>(
    GetInstallationPathDocument,
    options
  );
}
export type GetInstallationPathQueryHookResult = ReturnType<typeof useGetInstallationPathQuery>;
export type GetInstallationPathLazyQueryHookResult = ReturnType<typeof useGetInstallationPathLazyQuery>;
export type GetInstallationPathSuspenseQueryHookResult = ReturnType<typeof useGetInstallationPathSuspenseQuery>;
export type GetInstallationPathQueryResult = Apollo.QueryResult<GetInstallationPathQuery, GetInstallationPathQueryVariables>;
export function refetchGetInstallationPathQuery(variables?: GetInstallationPathQueryVariables) {
  return { query: GetInstallationPathDocument, variables: variables };
}
export const ConnectSlackUserDocument = gql`
  mutation ConnectSlackUser($secret: String!) {
    connect(secret: $secret) {
      slack_user_id
    }
  }
`;
export type ConnectSlackUserMutationFn = Apollo.MutationFunction<ConnectSlackUserMutation, ConnectSlackUserMutationVariables>;

/**
 * __useConnectSlackUserMutation__
 *
 * To run a mutation, you first call `useConnectSlackUserMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useConnectSlackUserMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [connectSlackUserMutation, { data, loading, error }] = useConnectSlackUserMutation({
 *   variables: {
 *      secret: // value for 'secret'
 *   },
 * });
 */
export function useConnectSlackUserMutation(
  baseOptions?: Apollo.MutationHookOptions<ConnectSlackUserMutation, ConnectSlackUserMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<ConnectSlackUserMutation, ConnectSlackUserMutationVariables>(ConnectSlackUserDocument, options);
}
export type ConnectSlackUserMutationHookResult = ReturnType<typeof useConnectSlackUserMutation>;
export type ConnectSlackUserMutationResult = Apollo.MutationResult<ConnectSlackUserMutation>;
export type ConnectSlackUserMutationOptions = Apollo.BaseMutationOptions<
  ConnectSlackUserMutation,
  ConnectSlackUserMutationVariables
>;
