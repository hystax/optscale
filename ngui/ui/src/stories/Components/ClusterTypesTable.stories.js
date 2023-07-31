import React from "react";
import { Provider } from "react-redux";
import configureMockStore from "redux-mock-store";
import { GET_ORGANIZATION_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import ClusterTypesTable from "components/ClusterTypesTable";
import { KINDS, MOCKED_ORGANIZATION_ID } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ClusterTypesTable`,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

const mockStore = configureMockStore();

const clusterTypes = [
  { name: "name1", tag_key: "tag1", priority: 1 },
  { name: "name2", tag_key: "tag2", priority: 2 }
];

export const withoutManageResourcePermission = (args) => (
  <ClusterTypesTable clusterTypes={clusterTypes} isLoading={args.isLoading} />
);

export const withManageResourcePermission = (args) => {
  const store = mockStore({
    organizationId: MOCKED_ORGANIZATION_ID,
    restapi: {
      [GET_ORGANIZATIONS]: {
        organizations: [
          {
            id: MOCKED_ORGANIZATION_ID
          }
        ]
      }
    },
    auth: {
      [GET_ORGANIZATION_ALLOWED_ACTIONS]: {
        allowedActions: {
          my_organization_id: ["MANAGE_RESOURCES"]
        }
      }
    }
  });

  return (
    <Provider store={store}>
      <ClusterTypesTable clusterTypes={clusterTypes} isLoading={args.isLoading} />
    </Provider>
  );
};
