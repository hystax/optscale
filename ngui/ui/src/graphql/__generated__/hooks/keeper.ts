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

export type Event = {
  __typename?: "Event";
  ack?: Maybe<Scalars["Boolean"]["output"]>;
  acknowledged_user?: Maybe<Scalars["String"]["output"]>;
  description?: Maybe<Scalars["String"]["output"]>;
  evt_class?: Maybe<Scalars["String"]["output"]>;
  id?: Maybe<Scalars["String"]["output"]>;
  level?: Maybe<Scalars["String"]["output"]>;
  localized?: Maybe<Scalars["String"]["output"]>;
  object_id?: Maybe<Scalars["String"]["output"]>;
  object_name?: Maybe<Scalars["String"]["output"]>;
  object_type?: Maybe<Scalars["String"]["output"]>;
  organization_id?: Maybe<Scalars["String"]["output"]>;
  read?: Maybe<Scalars["Boolean"]["output"]>;
  time?: Maybe<Scalars["Int"]["output"]>;
};

export type EventLevel = "DEBUG" | "ERROR" | "INFO" | "WARNING";

export type EventsRequestParams = {
  description_like?: InputMaybe<Scalars["String"]["input"]>;
  include_read?: InputMaybe<Scalars["Boolean"]["input"]>;
  last_id?: InputMaybe<Scalars["String"]["input"]>;
  level?: InputMaybe<Array<EventLevel>>;
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  read_on_get?: InputMaybe<Scalars["Boolean"]["input"]>;
  time_end?: InputMaybe<Scalars["Int"]["input"]>;
  time_start?: InputMaybe<Scalars["Int"]["input"]>;
};

export type Mutation = {
  __typename?: "Mutation";
  _empty?: Maybe<Scalars["String"]["output"]>;
};

export type Query = {
  __typename?: "Query";
  _empty?: Maybe<Scalars["String"]["output"]>;
  events?: Maybe<Array<Maybe<Event>>>;
};

export type QueryEventsArgs = {
  organizationId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<EventsRequestParams>;
};

export type EventsQueryVariables = Exact<{
  organizationId: Scalars["ID"]["input"];
  requestParams?: InputMaybe<EventsRequestParams>;
}>;

export type EventsQuery = {
  __typename?: "Query";
  events?: Array<{
    __typename?: "Event";
    time?: number | null;
    level?: string | null;
    evt_class?: string | null;
    object_id?: string | null;
    object_type?: string | null;
    object_name?: string | null;
    organization_id?: string | null;
    description?: string | null;
    ack?: boolean | null;
    localized?: string | null;
    id?: string | null;
    read?: boolean | null;
    acknowledged_user?: string | null;
  } | null> | null;
};

export const EventsDocument = gql`
  query events($organizationId: ID!, $requestParams: EventsRequestParams) {
    events(organizationId: $organizationId, requestParams: $requestParams) {
      time
      level
      evt_class
      object_id
      object_type
      object_name
      organization_id
      description
      ack
      localized
      id
      read
      acknowledged_user
    }
  }
`;

/**
 * __useEventsQuery__
 *
 * To run a query within a React component, call `useEventsQuery` and pass it any options that fit your needs.
 * When your component renders, `useEventsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useEventsQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      requestParams: // value for 'requestParams'
 *   },
 * });
 */
export function useEventsQuery(
  baseOptions: Apollo.QueryHookOptions<EventsQuery, EventsQueryVariables> &
    ({ variables: EventsQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<EventsQuery, EventsQueryVariables>(EventsDocument, options);
}
export function useEventsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<EventsQuery, EventsQueryVariables>) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<EventsQuery, EventsQueryVariables>(EventsDocument, options);
}
// @ts-ignore
export function useEventsSuspenseQuery(
  baseOptions?: Apollo.SuspenseQueryHookOptions<EventsQuery, EventsQueryVariables>
): Apollo.UseSuspenseQueryResult<EventsQuery, EventsQueryVariables>;
export function useEventsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<EventsQuery, EventsQueryVariables>
): Apollo.UseSuspenseQueryResult<EventsQuery | undefined, EventsQueryVariables>;
export function useEventsSuspenseQuery(
  baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<EventsQuery, EventsQueryVariables>
) {
  const options = baseOptions === Apollo.skipToken ? baseOptions : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<EventsQuery, EventsQueryVariables>(EventsDocument, options);
}
export type EventsQueryHookResult = ReturnType<typeof useEventsQuery>;
export type EventsLazyQueryHookResult = ReturnType<typeof useEventsLazyQuery>;
export type EventsSuspenseQueryHookResult = ReturnType<typeof useEventsSuspenseQuery>;
export type EventsQueryResult = Apollo.QueryResult<EventsQuery, EventsQueryVariables>;
export function refetchEventsQuery(variables: EventsQueryVariables) {
  return { query: EventsDocument, variables: variables };
}
