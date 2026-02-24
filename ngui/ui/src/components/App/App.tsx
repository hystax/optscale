import { Routes, Route, Navigate } from "react-router-dom";
import ErrorBoundary from "components/ErrorBoundary";
import LayoutWrapper from "components/LayoutWrapper";
import RoutePathContextProvider from "contexts/RoutePathContext/RoutePathContextProvider";
import { useGetToken } from "hooks/useGetToken";
import {
  INITIALIZE,
  LOGIN,
  NEXT_QUERY_PARAMETER_NAME,
  OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME,
  USER_EMAIL_QUERY_PARAMETER_NAME,
} from "urls";
import mainMenu from "utils/menus";
import { stringifySearchParams, getPathname, getSearchParams } from "utils/network";
import { isEmptyObject } from "utils/objects";
import { routes } from "utils/routes";

const RouteContent = ({ component, layout, context }) => (
  <LayoutWrapper component={component} layout={layout} context={context} mainMenu={mainMenu} />
);

const LoginNavigation = () => {
  const currentPathName = getPathname();
  const currentQueryParams = getSearchParams();

  const {
    [USER_EMAIL_QUERY_PARAMETER_NAME]: email,
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: capability,
    ...restQueryParams
  } = currentQueryParams as {
    [USER_EMAIL_QUERY_PARAMETER_NAME]: string;
    [OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME]: string;
  };

  const url = new URL(LOGIN, window.location.origin);

  if (currentPathName !== INITIALIZE) {
    url.searchParams.append(
      NEXT_QUERY_PARAMETER_NAME,
      `${currentPathName}${isEmptyObject(restQueryParams) ? "" : `?${stringifySearchParams(restQueryParams)}`}`
    );
  }

  if (email) {
    url.searchParams.append(USER_EMAIL_QUERY_PARAMETER_NAME, email);
  }

  if (capability) {
    url.searchParams.append(OPTSCALE_CAPABILITY_QUERY_PARAMETER_NAME, capability);
  }

  return <Navigate to={`${url.pathname}${url.search}`} />;
};

const RouteRender = ({ isTokenRequired, component, layout, context }) => {
  const { token } = useGetToken();

  // TODO: create a Page component and wrap each page explicitly with Redirector
  if (!token && isTokenRequired) {
    return <LoginNavigation />;
  }

  return (
    <ErrorBoundary>
      <RouteContent component={component} layout={layout} context={context} />
    </ErrorBoundary>
  );
};

const App = () => (
  <Routes>
    {routes.map(({ key, component, layout, link, isTokenRequired = true, context }) => (
      <Route
        key={key}
        path={link}
        element={
          <RoutePathContextProvider path={link}>
            <RouteRender isTokenRequired={isTokenRequired} component={component} context={context} layout={layout} />
          </RoutePathContextProvider>
        }
      />
    ))}
  </Routes>
);

export default App;
