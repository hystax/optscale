import { GraphQLResolveInfo } from "graphql";
import { ContextValue } from "../../../server";
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never };
export type RequireFields<T, K extends keyof T> = Omit<T, K> & { [P in K]-?: NonNullable<T[P]> };
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

export type ResolverTypeWrapper<T> = Promise<T> | T;

export type ResolverWithResolve<TResult, TParent, TContext, TArgs> = {
  resolve: ResolverFn<TResult, TParent, TContext, TArgs>;
};
export type Resolver<
  TResult,
  TParent = Record<PropertyKey, never>,
  TContext = Record<PropertyKey, never>,
  TArgs = Record<PropertyKey, never>,
> = ResolverFn<TResult, TParent, TContext, TArgs> | ResolverWithResolve<TResult, TParent, TContext, TArgs>;

export type ResolverFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => Promise<TResult> | TResult;

export type SubscriptionSubscribeFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => AsyncIterable<TResult> | Promise<AsyncIterable<TResult>>;

export type SubscriptionResolveFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

export interface SubscriptionSubscriberObject<TResult, TKey extends string, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<{ [key in TKey]: TResult }, TParent, TContext, TArgs>;
  resolve?: SubscriptionResolveFn<TResult, { [key in TKey]: TResult }, TContext, TArgs>;
}

export interface SubscriptionResolverObject<TResult, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<any, TParent, TContext, TArgs>;
  resolve: SubscriptionResolveFn<TResult, any, TContext, TArgs>;
}

export type SubscriptionObject<TResult, TKey extends string, TParent, TContext, TArgs> =
  | SubscriptionSubscriberObject<TResult, TKey, TParent, TContext, TArgs>
  | SubscriptionResolverObject<TResult, TParent, TContext, TArgs>;

export type SubscriptionResolver<
  TResult,
  TKey extends string,
  TParent = Record<PropertyKey, never>,
  TContext = Record<PropertyKey, never>,
  TArgs = Record<PropertyKey, never>,
> =
  | ((...args: any[]) => SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>)
  | SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>;

export type TypeResolveFn<TTypes, TParent = Record<PropertyKey, never>, TContext = Record<PropertyKey, never>> = (
  parent: TParent,
  context: TContext,
  info: GraphQLResolveInfo
) => Maybe<TTypes> | Promise<Maybe<TTypes>>;

export type IsTypeOfResolverFn<T = Record<PropertyKey, never>, TContext = Record<PropertyKey, never>> = (
  obj: T,
  context: TContext,
  info: GraphQLResolveInfo
) => boolean | Promise<boolean>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<
  TResult = Record<PropertyKey, never>,
  TParent = Record<PropertyKey, never>,
  TContext = Record<PropertyKey, never>,
  TArgs = Record<PropertyKey, never>,
> = (
  next: NextResolverFn<TResult>,
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

/** Mapping between all available schema types and the resolvers types */
export type ResolversTypes = {
  Boolean: ResolverTypeWrapper<Scalars["Boolean"]["output"]>;
  Event: ResolverTypeWrapper<Event>;
  EventLevel: EventLevel;
  EventsRequestParams: EventsRequestParams;
  ID: ResolverTypeWrapper<Scalars["ID"]["output"]>;
  Int: ResolverTypeWrapper<Scalars["Int"]["output"]>;
  Mutation: ResolverTypeWrapper<Record<PropertyKey, never>>;
  Query: ResolverTypeWrapper<Record<PropertyKey, never>>;
  String: ResolverTypeWrapper<Scalars["String"]["output"]>;
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Boolean: Scalars["Boolean"]["output"];
  Event: Event;
  EventsRequestParams: EventsRequestParams;
  ID: Scalars["ID"]["output"];
  Int: Scalars["Int"]["output"];
  Mutation: Record<PropertyKey, never>;
  Query: Record<PropertyKey, never>;
  String: Scalars["String"]["output"];
};

export type EventResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Event"] = ResolversParentTypes["Event"],
> = {
  ack?: Resolver<Maybe<ResolversTypes["Boolean"]>, ParentType, ContextType>;
  acknowledged_user?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  description?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  evt_class?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  id?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  level?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  localized?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  object_id?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  object_name?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  object_type?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  organization_id?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  read?: Resolver<Maybe<ResolversTypes["Boolean"]>, ParentType, ContextType>;
  time?: Resolver<Maybe<ResolversTypes["Int"]>, ParentType, ContextType>;
};

export type MutationResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Mutation"] = ResolversParentTypes["Mutation"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
};

export type QueryResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Query"] = ResolversParentTypes["Query"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  events?: Resolver<
    Maybe<Array<Maybe<ResolversTypes["Event"]>>>,
    ParentType,
    ContextType,
    RequireFields<QueryEventsArgs, "organizationId">
  >;
};

export type Resolvers<ContextType = ContextValue> = {
  Event?: EventResolvers<ContextType>;
  Mutation?: MutationResolvers<ContextType>;
  Query?: QueryResolvers<ContextType>;
};
