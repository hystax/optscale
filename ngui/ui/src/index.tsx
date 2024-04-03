import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import "intl-pluralrules";
import "core-js/stable";
import "text-security/text-security-disc.css";
import { createRoot } from "react-dom/client";
import { RawIntlProvider } from "react-intl";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { PersistGate } from "redux-persist/integration/react";
import ActivityListener from "components/ActivityListener";
import ApiErrorAlert from "components/ApiErrorAlert";
import ApiSuccessAlert from "components/ApiSuccessAlert";
import ApolloApiErrorAlert from "components/ApolloApiErrorAlert";
import ApolloProvider from "components/ApolloProvider";
import App from "components/App";
import SideModalManager from "components/SideModalManager";
import ThemeProviderWrapper from "components/ThemeProviderWrapper";
import Tour from "components/Tour";
import configureStore from "store";
import { intl } from "translations/react-intl-config";
import { microsoftOAuthConfiguration } from "utils/integrations";

const { store, persistor } = configureStore();

const pca = new PublicClientApplication(microsoftOAuthConfiguration);

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  // 10 Nov, 2023: google-map-react has been updated, verify the strinc mode.
  // <StrictMode>
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <RawIntlProvider value={intl}>
        <BrowserRouter>
          <ApolloProvider>
            <ActivityListener />
            <MsalProvider instance={pca}>
              <ThemeProviderWrapper>
                <SideModalManager>
                  <App />
                </SideModalManager>
                <Tour />
                <ApolloApiErrorAlert />
                <ApiErrorAlert />
                <ApiSuccessAlert />
              </ThemeProviderWrapper>
            </MsalProvider>
          </ApolloProvider>
        </BrowserRouter>
      </RawIntlProvider>
    </PersistGate>
  </Provider>
  // </StrictMode>
);
