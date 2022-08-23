import React from "react";
import { OrganizationOverviewMocked } from "components/OrganizationOverview";
import { EXPANDED_POOL_ROWS } from "components/PoolsTable/reducer";
import { MOCKED_ORGANIZATION_POOL_ID } from "mocks/idsMock";
import { boolean } from "@storybook/addon-knobs";
import { Provider } from "react-redux";
import { mockStore, MockState } from "utils/mockStore";
import { KINDS } from "stories";

export default {
  title: `${KINDS.MOCKUPS}/OrganizationOverviewMocked`
};

export const basic = () => {
  const withManagePoolPermission = boolean("with [MANAGE_POOLS] permission", false);
  const getPermissions = () => {
    const permissions = [];
    if (withManagePoolPermission) {
      permissions.push("MANAGE_POOLS");
    }
    return permissions;
  };

  const mockState = new MockState({
    [EXPANDED_POOL_ROWS]: [MOCKED_ORGANIZATION_POOL_ID, "7112961c-1225-4022-b529-029bfaee8e07"]
  });
  mockState.mockPoolPermissions(MOCKED_ORGANIZATION_POOL_ID, getPermissions());

  const store = mockStore(mockState);

  return (
    <Provider store={store}>
      <OrganizationOverviewMocked />
    </Provider>
  );
};
