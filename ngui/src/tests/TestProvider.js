import React from "react";
import PropTypes from "prop-types";
import { IntlProvider } from "react-intl";
import { Provider } from "react-redux";
import { unstable_HistoryRouter as HistoryRouter } from "react-router-dom";
import createMockStore from "redux-mock-store";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import apiMiddleware from "middleware/api";
import intlConfig from "translations/react-intl-config";
import history from "../history";

const mockStore = createMockStore([apiMiddleware]);

const TestProvider = ({ children, state = {} }) => {
  const store = mockStore(state);

  return (
    <Provider store={store}>
      <ThemeProviderWrapper>
        <IntlProvider {...intlConfig}>
          <HistoryRouter history={history}>{children}</HistoryRouter>
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
