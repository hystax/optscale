import React from "react";
import PropTypes from "prop-types";
import { Routes, Route, Navigate } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import ErrorBoundary from "components/ErrorBoundary";
import LayoutWrapper from "components/LayoutWrapper";
import { useApiData } from "hooks/useApiData";
import { useIsProfilingEnabled } from "hooks/useIsProfilingEnabled";
import { useOrganizationIdQueryParameterListener } from "hooks/useOrganizationIdQueryParameterListener";
import { getUrlWithNextQueryParam, LOGIN } from "urls";
import mainMenu from "utils/menus";
import { MAIN_MENU_SECTION_IDS } from "utils/menus/mainMenu";
import { getFullPath } from "utils/network";
import { routes } from "utils/routes";

const RouteContent = ({ component, layout, context }) => {
  const isMlProfilingEnabled = useIsProfilingEnabled();

  const excludedMainMenuSections = [...(isMlProfilingEnabled ? [] : [MAIN_MENU_SECTION_IDS.ML_PROFILING])];

  // By mapping a layout to menu we can make this prop might be dynamic depending on what menu we would like to display at each route
  return (
    <LayoutWrapper
      component={component}
      layout={layout}
      context={context}
      mainMenu={mainMenu.filter(({ id }) => !excludedMainMenuSections.includes(id))}
    />
  );
};

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
