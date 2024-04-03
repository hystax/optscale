import { gql } from "@apollo/client";

const GET_ERROR = gql`
  query GetError {
    error @client
  }
`;

export { GET_ERROR };
