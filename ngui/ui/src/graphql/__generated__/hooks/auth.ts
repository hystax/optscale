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
  StringArrayMap: { input: Record<string, string[]>; output: Record<string, string[]> };
};

export type Mutation = {
  __typename?: "Mutation";
  _empty?: Maybe<Scalars["String"]["output"]>;
  signIn?: Maybe<Token>;
  token?: Maybe<Token>;
  updateUser?: Maybe<Token>;
  user?: Maybe<User>;
};

export type MutationSignInArgs = {
  provider: Scalars["String"]["input"];
  redirectUri?: InputMaybe<Scalars["String"]["input"]>;
  tenantId?: InputMaybe<Scalars["String"]["input"]>;
  token: Scalars["String"]["input"];
};

export type MutationTokenArgs = {
  code?: InputMaybe<Scalars["String"]["input"]>;
  email: Scalars["String"]["input"];
  password?: InputMaybe<Scalars["String"]["input"]>;
};

export type MutationUpdateUserArgs = {
  id: Scalars["ID"]["input"];
  params: UpdateUserParams;
};

export type MutationUserArgs = {
  email: Scalars["String"]["input"];
  name: Scalars["String"]["input"];
  password: Scalars["String"]["input"];
};

export type OrganizationAllowedActionsRequestParams = {
  organization: Scalars["String"]["input"];
};

export type Query = {
  __typename?: "Query";
  _empty?: Maybe<Scalars["String"]["output"]>;
  organizationAllowedActions?: Maybe<Scalars["StringArrayMap"]["output"]>;
};

export type QueryOrganizationAllowedActionsArgs = {
  requestParams?: InputMaybe<OrganizationAllowedActionsRequestParams>;
};

export type Token = {
  __typename?: "Token";
  token?: Maybe<Scalars["String"]["output"]>;
  user_email: Scalars["String"]["output"];
  user_id: Scalars["ID"]["output"];
};

export type UpdateUserParams = {
  name?: InputMaybe<Scalars["String"]["input"]>;
  password?: InputMaybe<Scalars["String"]["input"]>;
};

export type User = {
  __typename?: "User";
  token?: Maybe<Scalars["String"]["output"]>;
  user_email: Scalars["String"]["output"];
  user_id: Scalars["ID"]["output"];
  verified: Scalars["Boolean"]["output"];
};

export type OrganizationAllowedActionsQueryVariables = Exact<{
  requestParams?: InputMaybe<OrganizationAllowedActionsRequestParams>;
}>;

export type OrganizationAllowedActionsQuery = {
  __typename?: "Query";
  organizationAllowedActions?: Record<string, string[]> | null;
};

export type CreateTokenMutationVariables = Exact<{
  email: Scalars["String"]["input"];
  password?: InputMaybe<Scalars["String"]["input"]>;
  code?: InputMaybe<Scalars["String"]["input"]>;
}>;

export type CreateTokenMutation = {
  __typename?: "Mutation";
  token?: { __typename?: "Token"; token?: string | null; user_id: string; user_email: string } | null;
};

export type CreateUserMutationVariables = Exact<{
  email: Scalars["String"]["input"];
  password: Scalars["String"]["input"];
  name: Scalars["String"]["input"];
}>;

export type CreateUserMutation = {
  __typename?: "Mutation";
  user?: { __typename?: "User"; token?: string | null; user_id: string; user_email: string; verified: boolean } | null;
};

export type SignInMutationVariables = Exact<{
  provider: Scalars["String"]["input"];
  token: Scalars["String"]["input"];
  tenantId?: InputMaybe<Scalars["String"]["input"]>;
  redirectUri?: InputMaybe<Scalars["String"]["input"]>;
}>;

export type SignInMutation = {
  __typename?: "Mutation";
  signIn?: { __typename?: "Token"; token?: string | null; user_id: string; user_email: string } | null;
};

export type UpdateUserMutationVariables = Exact<{
  id: Scalars["ID"]["input"];
  params: UpdateUserParams;
}>;

export type UpdateUserMutation = {
  __typename?: "Mutation";
  updateUser?: { __typename?: "Token"; token?: string | null; user_id: string; user_email: string } | null;
};

export const OrganizationAllowedActionsDocument = gql`
  query OrganizationAllowedActions($requestParams: OrganizationAllowedActionsRequestParams) {
    organizationAllowedActions(requestParams: $requestParams)
  }
`;

/**
 * __useOrganizationAllowedActionsQuery__
 *
 * To run a query within a React component, call `useOrganizationAllowedActionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationAllowedActionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationAllowedActionsQuery({
 *   variables: {
 *      requestParams: // value for 'requestParams'
 *   },
 * });
 */
export function useOrganizationAllowedActionsQuery(
  baseOptions?: Apollo.QueryHookOptions<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>(
    OrganizationAllowedActionsDocument,
    options
  );
}
export function useOrganizationAllowedActionsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>(
    OrganizationAllowedActionsDocument,
    options
  );
}
// @ts-ignore
export function useOrganizationAllowedActionsSuspenseQuery(
  baseOptions?: Apollo.SuspenseQueryHookOptions<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>
): Apollo.UseSuspenseQueryResult<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>;
export function useOrganizationAllowedActionsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>
): Apollo.UseSuspenseQueryResult<OrganizationAllowedActionsQuery | undefined, OrganizationAllowedActionsQueryVariables>;
export function useOrganizationAllowedActionsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<OrganizationAllowedActionsQuery, OrganizationAllowedActionsQueryVariables>(
    OrganizationAllowedActionsDocument,
    options
  );
}
export type OrganizationAllowedActionsQueryHookResult = ReturnType<typeof useOrganizationAllowedActionsQuery>;
export type OrganizationAllowedActionsLazyQueryHookResult = ReturnType<typeof useOrganizationAllowedActionsLazyQuery>;
export type OrganizationAllowedActionsSuspenseQueryHookResult = ReturnType<typeof useOrganizationAllowedActionsSuspenseQuery>;
export type OrganizationAllowedActionsQueryResult = Apollo.QueryResult<
  OrganizationAllowedActionsQuery,
  OrganizationAllowedActionsQueryVariables
>;
export function refetchOrganizationAllowedActionsQuery(variables?: OrganizationAllowedActionsQueryVariables) {
  return { query: OrganizationAllowedActionsDocument, variables: variables };
}
export const CreateTokenDocument = gql`
  mutation CreateToken($email: String!, $password: String, $code: String) {
    token(email: $email, password: $password, code: $code) {
      token
      user_id
      user_email
    }
  }
`;
export type CreateTokenMutationFn = Apollo.MutationFunction<CreateTokenMutation, CreateTokenMutationVariables>;

/**
 * __useCreateTokenMutation__
 *
 * To run a mutation, you first call `useCreateTokenMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateTokenMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createTokenMutation, { data, loading, error }] = useCreateTokenMutation({
 *   variables: {
 *      email: // value for 'email'
 *      password: // value for 'password'
 *      code: // value for 'code'
 *   },
 * });
 */
export function useCreateTokenMutation(
  baseOptions?: Apollo.MutationHookOptions<CreateTokenMutation, CreateTokenMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<CreateTokenMutation, CreateTokenMutationVariables>(CreateTokenDocument, options);
}
export type CreateTokenMutationHookResult = ReturnType<typeof useCreateTokenMutation>;
export type CreateTokenMutationResult = Apollo.MutationResult<CreateTokenMutation>;
export type CreateTokenMutationOptions = Apollo.BaseMutationOptions<CreateTokenMutation, CreateTokenMutationVariables>;
export const CreateUserDocument = gql`
  mutation CreateUser($email: String!, $password: String!, $name: String!) {
    user(email: $email, password: $password, name: $name) {
      token
      user_id
      user_email
      verified
    }
  }
`;
export type CreateUserMutationFn = Apollo.MutationFunction<CreateUserMutation, CreateUserMutationVariables>;

/**
 * __useCreateUserMutation__
 *
 * To run a mutation, you first call `useCreateUserMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateUserMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createUserMutation, { data, loading, error }] = useCreateUserMutation({
 *   variables: {
 *      email: // value for 'email'
 *      password: // value for 'password'
 *      name: // value for 'name'
 *   },
 * });
 */
export function useCreateUserMutation(
  baseOptions?: Apollo.MutationHookOptions<CreateUserMutation, CreateUserMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<CreateUserMutation, CreateUserMutationVariables>(CreateUserDocument, options);
}
export type CreateUserMutationHookResult = ReturnType<typeof useCreateUserMutation>;
export type CreateUserMutationResult = Apollo.MutationResult<CreateUserMutation>;
export type CreateUserMutationOptions = Apollo.BaseMutationOptions<CreateUserMutation, CreateUserMutationVariables>;
export const SignInDocument = gql`
  mutation SignIn($provider: String!, $token: String!, $tenantId: String, $redirectUri: String) {
    signIn(provider: $provider, token: $token, tenantId: $tenantId, redirectUri: $redirectUri) {
      token
      user_id
      user_email
    }
  }
`;
export type SignInMutationFn = Apollo.MutationFunction<SignInMutation, SignInMutationVariables>;

/**
 * __useSignInMutation__
 *
 * To run a mutation, you first call `useSignInMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSignInMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [signInMutation, { data, loading, error }] = useSignInMutation({
 *   variables: {
 *      provider: // value for 'provider'
 *      token: // value for 'token'
 *      tenantId: // value for 'tenantId'
 *      redirectUri: // value for 'redirectUri'
 *   },
 * });
 */
export function useSignInMutation(baseOptions?: Apollo.MutationHookOptions<SignInMutation, SignInMutationVariables>) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<SignInMutation, SignInMutationVariables>(SignInDocument, options);
}
export type SignInMutationHookResult = ReturnType<typeof useSignInMutation>;
export type SignInMutationResult = Apollo.MutationResult<SignInMutation>;
export type SignInMutationOptions = Apollo.BaseMutationOptions<SignInMutation, SignInMutationVariables>;
export const UpdateUserDocument = gql`
  mutation UpdateUser($id: ID!, $params: UpdateUserParams!) {
    updateUser(id: $id, params: $params) {
      token
      user_id
      user_email
    }
  }
`;
export type UpdateUserMutationFn = Apollo.MutationFunction<UpdateUserMutation, UpdateUserMutationVariables>;

/**
 * __useUpdateUserMutation__
 *
 * To run a mutation, you first call `useUpdateUserMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateUserMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateUserMutation, { data, loading, error }] = useUpdateUserMutation({
 *   variables: {
 *      id: // value for 'id'
 *      params: // value for 'params'
 *   },
 * });
 */
export function useUpdateUserMutation(
  baseOptions?: Apollo.MutationHookOptions<UpdateUserMutation, UpdateUserMutationVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<UpdateUserMutation, UpdateUserMutationVariables>(UpdateUserDocument, options);
}
export type UpdateUserMutationHookResult = ReturnType<typeof useUpdateUserMutation>;
export type UpdateUserMutationResult = Apollo.MutationResult<UpdateUserMutation>;
export type UpdateUserMutationOptions = Apollo.BaseMutationOptions<UpdateUserMutation, UpdateUserMutationVariables>;
