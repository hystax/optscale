import { Routes, Route, Navigate } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import ErrorBoundary from "components/ErrorBoundary";
import LayoutWrapper from "components/LayoutWrapper";
import CommunityDocsContextProvider from "contexts/CommunityDocsContext/CommunityDocsContextProvider";
import { useApiData } from "hooks/useApiData";
import { useOrganizationIdQueryParameterListener } from "hooks/useOrganizationIdQueryParameterListener";
import { LOGIN, USER_EMAIL_QUERY_PARAMETER_NAME } from "urls";
import mainMenu from "utils/menus";
import { formQueryString, getPathname, getQueryParams } from "utils/network";
import { isEmpty } from "utils/objects";
import { routes } from "utils/routes";

const RouteContent = ({ component, layout, context }) => (
  <LayoutWrapper component={component} layout={layout} context={context} mainMenu={mainMenu} />
);

const LoginNavigation = () => {
  const currentPathName = getPathname();
  const currentQueryParams = getQueryParams();

  const { [USER_EMAIL_QUERY_PARAMETER_NAME]: email, ...restQueryParams } = currentQueryParams;

  const getNextParameter = () => {
    const nextRoute = currentPathName;
    const nextRouteQueryParams = isEmpty(restQueryParams) ? "" : `?${formQueryString(restQueryParams).replace(/&/g, "%26")}`;

    return `next=${nextRoute}${nextRouteQueryParams}`;
  };

  const getEmailParameter = () => `${USER_EMAIL_QUERY_PARAMETER_NAME}=${email}`;

  const parametersString = [getNextParameter(), ...(email ? [getEmailParameter()] : [])].join("&");

  const to = `${LOGIN}?${parametersString}`;

  return <Navigate to={to} />;
};

const RouteRender = ({ isTokenRequired, component, layout, context }) => {
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  useOrganizationIdQueryParameterListener();

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
  <CommunityDocsContextProvider>
    <Routes>
      {routes.map(({ key, component, layout, link, isTokenRequired = true, context }) => (
        <Route
          key={key}
          path={link}
          element={<RouteRender isTokenRequired={isTokenRequired} component={component} context={context} layout={layout} />}
        />
      ))}
    </Routes>
  </CommunityDocsContextProvider>
);

export default App;
