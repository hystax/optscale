import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { text } from "@storybook/addon-knobs";
import { addDecorator, addParameters } from "@storybook/react";
import intlConfig from "translations/react-intl-config";
import { MockState, mockStore } from "utils/mockStore";
import { splitAndTrim } from "utils/strings";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import { IntlProvider } from "react-intl";
import { MOCKED_ORGANIZATION_POOL_ID, MOCKED_RESOURCE_ID, MOCKED_ORGANIZATION_ID } from "mocks/idsMock";
import { KINDS, MockPermissionsStateContext } from "stories";
import { Provider } from "react-redux";

// TODO - find out how to add font dependency to storybook, take a look at https://storybook.js.org/docs/react/essentials/viewport
addDecorator((story) => <ThemeProviderWrapper>{story()}</ThemeProviderWrapper>);
addDecorator((story) => <IntlProvider {...intlConfig}>{story()}</IntlProvider>);
addDecorator((story) => <Provider store={mockStore({ state: {} })}>{story()}</Provider>);
addDecorator((story, { kind }) => {
  const [storyKind] = kind.split("/");

  if (storyKind === KINDS.PAGES) {
    const organizationAllowedActions = text("Organization allowed actions");
    const poolAllowedActions = text("Pool allowed actions");
    const resourceAllowedActions = text("Resource allowed actions");

    const getResourceAllowedActions = () => {
      return splitAndTrim(resourceAllowedActions);
    };

    const getOrganizationAllowedActions = () => {
      return splitAndTrim(organizationAllowedActions);
    };

    const getPoolAllowedActions = () => {
      return splitAndTrim(poolAllowedActions);
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

  return story();
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
