import { GraphQLResolveInfo, GraphQLScalarType, GraphQLScalarTypeConfig } from "graphql";
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
  ID: ResolverTypeWrapper<Scalars["ID"]["output"]>;
  Mutation: ResolverTypeWrapper<Record<PropertyKey, never>>;
  OrganizationAllowedActionsRequestParams: OrganizationAllowedActionsRequestParams;
  Query: ResolverTypeWrapper<Record<PropertyKey, never>>;
  String: ResolverTypeWrapper<Scalars["String"]["output"]>;
  StringArrayMap: ResolverTypeWrapper<Scalars["StringArrayMap"]["output"]>;
  Token: ResolverTypeWrapper<Token>;
  UpdateUserParams: UpdateUserParams;
  User: ResolverTypeWrapper<User>;
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Boolean: Scalars["Boolean"]["output"];
  ID: Scalars["ID"]["output"];
  Mutation: Record<PropertyKey, never>;
  OrganizationAllowedActionsRequestParams: OrganizationAllowedActionsRequestParams;
  Query: Record<PropertyKey, never>;
  String: Scalars["String"]["output"];
  StringArrayMap: Scalars["StringArrayMap"]["output"];
  Token: Token;
  UpdateUserParams: UpdateUserParams;
  User: User;
};

export type MutationResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Mutation"] = ResolversParentTypes["Mutation"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  signIn?: Resolver<
    Maybe<ResolversTypes["Token"]>,
    ParentType,
    ContextType,
    RequireFields<MutationSignInArgs, "provider" | "token">
  >;
  token?: Resolver<Maybe<ResolversTypes["Token"]>, ParentType, ContextType, RequireFields<MutationTokenArgs, "email">>;
  updateUser?: Resolver<
    Maybe<ResolversTypes["Token"]>,
    ParentType,
    ContextType,
    RequireFields<MutationUpdateUserArgs, "id" | "params">
  >;
  user?: Resolver<
    Maybe<ResolversTypes["User"]>,
    ParentType,
    ContextType,
    RequireFields<MutationUserArgs, "email" | "name" | "password">
  >;
};

export type QueryResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Query"] = ResolversParentTypes["Query"],
> = {
  _empty?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  organizationAllowedActions?: Resolver<
    Maybe<ResolversTypes["StringArrayMap"]>,
    ParentType,
    ContextType,
    Partial<QueryOrganizationAllowedActionsArgs>
  >;
};

export interface StringArrayMapScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes["StringArrayMap"], any> {
  name: "StringArrayMap";
}

export type TokenResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["Token"] = ResolversParentTypes["Token"],
> = {
  token?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  user_email?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  user_id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
};

export type UserResolvers<
  ContextType = ContextValue,
  ParentType extends ResolversParentTypes["User"] = ResolversParentTypes["User"],
> = {
  token?: Resolver<Maybe<ResolversTypes["String"]>, ParentType, ContextType>;
  user_email?: Resolver<ResolversTypes["String"], ParentType, ContextType>;
  user_id?: Resolver<ResolversTypes["ID"], ParentType, ContextType>;
  verified?: Resolver<ResolversTypes["Boolean"], ParentType, ContextType>;
};

export type Resolvers<ContextType = ContextValue> = {
  Mutation?: MutationResolvers<ContextType>;
  Query?: QueryResolvers<ContextType>;
  StringArrayMap?: GraphQLScalarType;
  Token?: TokenResolvers<ContextType>;
  User?: UserResolvers<ContextType>;
};
