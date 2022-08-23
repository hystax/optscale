import React from "react";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import ReactDOM from "react-dom";
import "intl-pluralrules";
import "core-js/stable";
import "regenerator-runtime/runtime";
import "text-security/text-security-disc.css";
import { RawIntlProvider } from "react-intl";
import { Provider } from "react-redux";
import { unstable_HistoryRouter as HistoryRouter } from "react-router-dom";
import { PersistGate } from "redux-persist/integration/react";
import ActivityListener from "components/ActivityListener";
import ApiErrorAlert from "components/ApiErrorAlert";
import ApiSuccessAlert from "components/ApiSuccessAlert";
import App from "components/App";
import SideModalManager from "components/SideModalManager";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import OrganizationChangeListener from "containers/OrganizationChangeListener";
import PendingInvitationsAlertContainer from "containers/PendingInvitationsAlertContainer";
import * as serviceWorker from "serviceWorker";
import configureStore from "store";
import { intl } from "translations/react-intl-config";
import { microsoftOAuthConfiguration } from "utils/integrations";
import history from "./history";

const { store, persistor } = configureStore();

const pca = new PublicClientApplication(microsoftOAuthConfiguration);

ReactDOM.render(
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <RawIntlProvider value={intl}>
        <HistoryRouter history={history}>
          <ActivityListener />
          <OrganizationChangeListener>
            <MsalProvider instance={pca}>
              <ThemeProviderWrapper>
                <SideModalManager>
                  <App />
                </SideModalManager>
                <ApiErrorAlert />
                <ApiSuccessAlert />
                <PendingInvitationsAlertContainer />
              </ThemeProviderWrapper>
            </MsalProvider>
          </OrganizationChangeListener>
        </HistoryRouter>
      </RawIntlProvider>
    </PersistGate>
  </Provider>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
