import React from "react";
import ClusterTypesTable from "components/ClusterTypesTable";
import configureMockStore from "redux-mock-store";
import { Provider } from "react-redux";
import { GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { GET_ORGANIZATION_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { MOCKED_ORGANIZATION_ID } from "mocks/idsMock";
import { boolean } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ClusterTypesTable`
};

const mockStore = configureMockStore();

const clusterTypes = [
  { name: "name1", tag_key: "tag1", priority: 1 },
  { name: "name2", tag_key: "tag2", priority: 2 }
];

export const withoutManageResourcePermission = () => (
  <ClusterTypesTable clusterTypes={clusterTypes} isLoading={boolean("isLoading", false)} />
);

export const withManageResourcePermission = () => {
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
      <ClusterTypesTable clusterTypes={clusterTypes} isLoading={boolean("isLoading", false)} />
    </Provider>
  );
};
