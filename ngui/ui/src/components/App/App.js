import React from "react";
import PropTypes from "prop-types";
import { Routes, Route, Navigate } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import ErrorBoundary from "components/ErrorBoundary";
import LayoutWrapper from "components/LayoutWrapper";
import { useApiData } from "hooks/useApiData";
import { useOrganizationIdQueryParameterListener } from "hooks/useOrganizationIdQueryParameterListener";
import { useRootData } from "hooks/useRootData";
import { SIGNOUT_OPTIONS } from "reducers/signoutOptions/reducer";
import { LOGIN } from "urls";
import mainMenu from "utils/menus";
import { routes } from "utils/routes";

const RouteContent = ({ component, layout, context }) => (
  <LayoutWrapper component={component} layout={layout} context={context} mainMenu={mainMenu} />
);

const LoginNavigation = () => {
  const {
    rootData: { next, userEmail }
  } = useRootData(SIGNOUT_OPTIONS);

  const to = `${LOGIN}?next=${next}&userEmail=${userEmail}`;

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

RouteRender.propTypes = {
  isTokenRequired: PropTypes.bool.isRequired,
  component: PropTypes.elementType,
  layout: PropTypes.elementType,
  context: PropTypes.object
};

const App = () => (
  <Routes>
    {routes.map(({ key, component, layout, link, isTokenRequired = true, context }) => (
      <Route
        key={key}
        path={link}
        element={<RouteRender isTokenRequired={isTokenRequired} component={component} context={context} layout={layout} />}
      />
    ))}
  </Routes>
);

export default App;
