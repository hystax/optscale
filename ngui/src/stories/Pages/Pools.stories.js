import React from "react";
import { MOCKED_ORGANIZATION_POOL_ID } from "mocks/idsMock";
import { OrganizationOverviewMocked } from "components/OrganizationOverview";
import { EXPANDED_POOL_ROWS } from "components/PoolsTable/reducer";
import { Provider } from "react-redux";
import { mockStore, MockState } from "utils/mockStore";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/Pools`
};

export const basic = () => {
  const mockState = new MockState({
    [EXPANDED_POOL_ROWS]: [MOCKED_ORGANIZATION_POOL_ID, "7112961c-1225-4022-b529-029bfaee8e07"]
  });

  const store = mockStore(mockState);

  return (
    <Provider store={store}>
      <OrganizationOverviewMocked />
    </Provider>
  );
};
