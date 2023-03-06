import React from "react";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import "intl-pluralrules";
import "core-js/stable";
import "regenerator-runtime/runtime";
import "text-security/text-security-disc.css";
import { createRoot } from "react-dom/client";
import { RawIntlProvider } from "react-intl";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { PersistGate } from "redux-persist/integration/react";
import ActivityListener from "components/ActivityListener";
import ApiErrorAlert from "components/ApiErrorAlert";
import ApiSuccessAlert from "components/ApiSuccessAlert";
import App from "components/App";
import SideModalManager from "components/SideModalManager";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import Tour from "components/Tour";
import * as serviceWorker from "serviceWorker";
import configureStore from "store";
import { intl } from "translations/react-intl-config";
import { microsoftOAuthConfiguration } from "utils/integrations";

const { store, persistor } = configureStore();

const pca = new PublicClientApplication(microsoftOAuthConfiguration);

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  // Enable when google-map-react supports strict mode
  // <StrictMode>
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <RawIntlProvider value={intl}>
        <BrowserRouter>
          <ActivityListener />
          <MsalProvider instance={pca}>
            <ThemeProviderWrapper>
              <SideModalManager>
                <App />
              </SideModalManager>
              <Tour />
              <ApiErrorAlert />
              <ApiSuccessAlert />
            </ThemeProviderWrapper>
          </MsalProvider>
        </BrowserRouter>
      </RawIntlProvider>
    </PersistGate>
  </Provider>
  // </StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
