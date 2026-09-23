import { GraphQLScalarType } from "graphql";
import { Resolvers } from "../__generated__/types/auth";

const resolvers: Resolvers = {
  StringArrayMap: new GraphQLScalarType({
    name: "StringArrayMap",
    description: "Represents an object where each key maps to an array of strings, e.g. { 'org1': ['read', 'write'] }",
    serialize(value) {
      if (typeof value !== "object" || value === null) {
        throw new TypeError("StringArrayMap must be an object");
      }

      for (const v of Object.values(value)) {
        if (!Array.isArray(v) || v.some((x) => typeof x !== "string")) {
          throw new TypeError("All values in StringArrayMap must be string arrays");
        }
      }

      return value;
    },
    parseValue(value) {
      if (typeof value !== "object" || value === null) {
        throw new TypeError("Invalid input for StringArrayMap");
      }
      return value;
    },
  }),
  Query: {
    organizationAllowedActions: async (_, { requestParams }, { dataSources }) => {
      return dataSources.auth.getOrganizationAllowedActions(requestParams);
    },
  },
  Mutation: {
    token: async (_, { email, password, code }, { dataSources }) => {
      return dataSources.auth.createToken({ email, password, code });
    },
    user: async (_, { email, password, name }, { dataSources }) => {
      return dataSources.auth.createUser(email, password, name);
    },
    updateUser: async (_, { id, params }, { dataSources }) => {
      return dataSources.auth.updateUser(id, params);
    },
    signIn: async (_, { provider, token, tenantId, redirectUri }, { dataSources }) => {
      return dataSources.auth.signIn(provider, token, tenantId, redirectUri);
    },
  },
};

export default resolvers;
