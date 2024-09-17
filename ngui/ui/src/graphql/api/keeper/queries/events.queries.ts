import { gql } from "@apollo/client";

const GET_EVENTS = gql`
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

export { GET_EVENTS };
