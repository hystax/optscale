import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { addDecorator, addParameters } from "@storybook/react";
import intlConfig from "translations/react-intl-config";
import { MockState, mockStore } from "utils/mockStore";
import { splitAndTrim } from "utils/strings";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import { IntlProvider } from "react-intl";
import {
  KINDS,
  MOCKED_ORGANIZATION_POOL_ID,
  MOCKED_RESOURCE_ID,
  MOCKED_ORGANIZATION_ID,
  MockPermissionsStateContext
} from "stories";
import { Provider } from "react-redux";

// TODO - find out how to add font dependency to storybook, take a look at https://storybook.js.org/docs/react/essentials/viewport
addDecorator((story) => <ThemeProviderWrapper>{story()}</ThemeProviderWrapper>);
addDecorator((story) => <IntlProvider {...intlConfig}>{story()}</IntlProvider>);
addDecorator((story) => <Provider store={mockStore({ state: {} })}>{story()}</Provider>);
addDecorator((story, { kind, argTypes }) => {
  const [storyKind] = kind.split("/");

  if (storyKind === KINDS.PAGES) {
    const getResourceAllowedActions = () => {
      return splitAndTrim(argTypes.resourceAllowedActions.defaultValue);
    };

    const getOrganizationAllowedActions = () => {
      return splitAndTrim(argTypes.organizationAllowedActions.defaultValue);
    };

    const getPoolAllowedActions = () => {
      return splitAndTrim(argTypes.poolAllowedActions.defaultValue);
    };

    const mockState = new MockState();
    mockState.mockOrganizationPermissions(MOCKED_ORGANIZATION_ID, getOrganizationAllowedActions());
    mockState.mockPoolPermissions(MOCKED_ORGANIZATION_POOL_ID, getPoolAllowedActions());
    mockState.mockResourcePermissions(MOCKED_RESOURCE_ID, getResourceAllowedActions());

    return (
      <MockPermissionsStateContext.Provider
        value={{
          mockStore,
          mockState
        }}
      >
        {story()}
      </MockPermissionsStateContext.Provider>
    );
  }

  return story(argTypes);
});
addDecorator((story) => <Router>{story()}</Router>);
addParameters({
  backgrounds: {
    default: "OptScale",
    values: [
      {
        name: "OptScale",
        // TODO: Get BACKGROUND color from theme
        value: "rgb(246, 247, 248)"
      }
    ]
  }
});

export const argTypes = {
  organizationAllowedActions: { name: "Organization allowed actions", control: "text", defaultValue: "" },
  poolAllowedActions: { name: "Pool allowed actions", control: "text", defaultValue: "" },
  resourceAllowedActions: { name: "Resource allowed actions", control: "text", defaultValue: "" }
};
