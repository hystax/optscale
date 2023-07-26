import React from "react";
import PropTypes from "prop-types";
import { IntlProvider } from "react-intl";
import { Provider } from "react-redux";
import { MemoryRouter } from "react-router-dom";
import createMockStore from "redux-mock-store";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import apiMiddleware from "middleware/api";
import intlConfig from "translations/react-intl-config";

const mockStore = createMockStore([apiMiddleware]);

const TestProvider = ({ children, state = {} }) => {
  const store = mockStore(state);

  return (
    <Provider store={store}>
      <ThemeProviderWrapper>
        <IntlProvider {...intlConfig}>
          <MemoryRouter>{children}</MemoryRouter>
        </IntlProvider>
      </ThemeProviderWrapper>
    </Provider>
  );
};

TestProvider.propTypes = {
  children: PropTypes.node.isRequired,
  state: PropTypes.object
};

export default TestProvider;
