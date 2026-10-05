import { gql } from "graphql-tag";

export default gql`
  input OrganizationAllowedActionsRequestParams {
    organization: String!
  }

  type Token {
    user_email: String!
    user_id: ID!
    token: String
  }

  type User {
    user_email: String!
    user_id: ID!
    token: String
    verified: Boolean!
  }

  scalar StringArrayMap

  type Query {
    organizationAllowedActions(requestParams: OrganizationAllowedActionsRequestParams): StringArrayMap
  }

  input UpdateUserParams {
    password: String
    name: String
  }

  input UtmParams {
    utm_source: String
    utm_medium: String
    utm_campaign: String
    utm_term: String
    utm_content: String
  }

  type Mutation {
    token(email: String!, password: String, code: String): Token
    user(email: String!, password: String!, name: String!, utm: UtmParams): User
    updateUser(id: ID!, params: UpdateUserParams!): Token
    signIn(provider: String!, token: String!, tenantId: String, redirectUri: String, utm: UtmParams): Token
  }
`;
