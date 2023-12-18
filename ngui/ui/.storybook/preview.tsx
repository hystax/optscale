import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import intlConfig from "../src/translations/react-intl-config";
import { MockState } from "../src/utils/MockState";
import { splitAndTrim } from "../src/utils/strings";
import ThemeProviderWrapper from "../src/components/ThemeProviderWrapper";
import { IntlProvider } from "react-intl";
import {
  MOCKED_ORGANIZATION_POOL_ID,
  MOCKED_RESOURCE_ID,
  MOCKED_ORGANIZATION_ID,
  MockPermissionsStateContext
} from "../src/stories";
import { Provider } from "react-redux";
import type { Preview } from "@storybook/react";
import configureMockStore from "redux-mock-store";

const preview: Preview = {
  argTypes: {
    organizationAllowedActions: { name: "Organization allowed actions", control: "text", defaultValue: "" },
    poolAllowedActions: { name: "Pool allowed actions", control: "text", defaultValue: "" },
    resourceAllowedActions: { name: "Resource allowed actions", control: "text", defaultValue: "" }
  },
  parameters: {
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
  },
  decorators: [
    (Story) => {
      const mockStore = configureMockStore();

      return (
        <Provider store={mockStore({ state: {} })}>
          <IntlProvider {...intlConfig}>
            <Router>
              <ThemeProviderWrapper>
                <Story />
              </ThemeProviderWrapper>
            </Router>
          </IntlProvider>
        </Provider>
      );
    },
    (Story, { title, argTypes, ...rest }) => {
      const [storyRoot] = title.split("/");
      if (storyRoot === "Pages") {
        const getResourceAllowedActions = () => {
          return splitAndTrim(argTypes.resourceAllowedActions.defaultValue);
        };
        const getOrganizationAllowedActions = () => {
          return splitAndTrim(argTypes.organizationAllowedActions.defaultValue);
        };
        const getPoolAllowedActions = () => {
          return splitAndTrim(argTypes.poolAllowedActions.defaultValue);
        };

        const mockState = MockState();

        mockState.mockOrganizationPermissions(MOCKED_ORGANIZATION_ID, getOrganizationAllowedActions());
        mockState.mockPoolPermissions(MOCKED_ORGANIZATION_POOL_ID, getPoolAllowedActions());
        mockState.mockResourcePermissions(MOCKED_RESOURCE_ID, getResourceAllowedActions());

        const mockStore = configureMockStore();

        return (
          <MockPermissionsStateContext.Provider
            value={{
              mockStore,
              mockState
            }}
          >
            <Story />
          </MockPermissionsStateContext.Provider>
        );
      }
      return <Story />;
    }
  ]
};

export default preview;
