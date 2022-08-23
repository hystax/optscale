import React from "react";
import PropTypes from "prop-types";
import { Routes, Route, Navigate } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import ErrorBoundary from "components/ErrorBoundary";
import LayoutWrapper from "components/LayoutWrapper";
import { useApiData } from "hooks/useApiData";
import { useOrganizationIdQueryParameterListener } from "hooks/useOrganizationIdQueryParameterListener";
import routes from "routes";
import { getUrlWithNextQueryParam, LOGIN } from "urls";
import { getFullPath } from "utils/network";

const RouteRender = ({ isTokenRequired, component, layout, context }) => {
  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  useOrganizationIdQueryParameterListener();

  // TODO: create a Page component and wrap each page explicitly with Redirector
  if (!token && isTokenRequired) {
    const to = getUrlWithNextQueryParam(LOGIN, getFullPath(), true);
    return <Navigate to={to} />;
  }

  return (
    <ErrorBoundary>
      <LayoutWrapper component={component} layout={layout} context={context} />
    </ErrorBoundary>
  );
};

RouteRender.propTypes = {
  isTokenRequired: PropTypes.bool.isRequired,
  redirectIfTokenNotExists: PropTypes.shape({
    getPath: PropTypes.func,
    push: PropTypes.bool
  }),
  redirectIfTokenExists: PropTypes.shape({
    getPath: PropTypes.func
  }),
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
