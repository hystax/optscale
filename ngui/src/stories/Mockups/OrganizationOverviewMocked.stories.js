import React from "react";
import { Provider } from "react-redux";
import { OrganizationOverviewMocked } from "components/OrganizationOverview";
import { EXPANDED_POOL_ROWS } from "components/PoolsTable/reducer";
import { KINDS, MOCKED_ORGANIZATION_POOL_ID } from "stories";
import { mockStore, MockState } from "utils/mockStore";

export default {
  title: `${KINDS.MOCKUPS}/OrganizationOverviewMocked`,
  argTypes: {
    withManagePoolsPermission: { name: "With MANAGE_POOLS permission", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => {
  const withManagePoolPermission = args.withManagePoolsPermission;
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
