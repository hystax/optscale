import { gql } from "@apollo/client";

const GET_INSTALLATION_PATH = gql`
  query GetInstallationPath {
    url
  }
`;

const CONNECT_SLACK_USER = gql`
  mutation ConnectSlackUser($secret: String!) {
    connect(secret: $secret) {
      slack_user_id
    }
  }
`;

export { GET_INSTALLATION_PATH, CONNECT_SLACK_USER };
