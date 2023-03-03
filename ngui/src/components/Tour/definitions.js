import React from "react";
import { FormattedMessage } from "react-intl";

import {
  ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS,
  ENVIRONMENT_SOFTWARE_FIELD,
  ENVIRONMENT_JIRA_TICKETS_FIELD
} from "utils/constants";
import { ENVIRONMENTS_TOUR, PRODUCT_TOUR } from "./reducer";

export const ENVIRONMENTS_TOUR_IDS = {
  HEADER: "environmentsPageHeader",
  ADD_BUTTON: "environmentsAddButton",
  STATUS_CELL: "environmentsStatus",
  JIRA_CELL: "environmentsJiraTickets",
  SOFT_CELL: "environmentsSoftware"
};

const ENVIRONMENTS_TOUR_STEPS = [
  {
    id: ENVIRONMENTS_TOUR_IDS.HEADER,
    target: ENVIRONMENTS_TOUR_IDS.HEADER,
    content: (
      <FormattedMessage id="environmentsPageHeaderTourContent" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
    ),
    dataTestId: "tour-environments-page-header"
  },
  {
    id: ENVIRONMENTS_TOUR_IDS.ADD_BUTTON,
    target: ENVIRONMENTS_TOUR_IDS.ADD_BUTTON,
    content: (
      <FormattedMessage id="environmentsAddButtonTourContent" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
    ),
    dataTestId: "tour-environments-add-button",
    missable: true
  },
  {
    id: ENVIRONMENTS_TOUR_IDS.STATUS_CELL,
    target: ENVIRONMENTS_TOUR_IDS.STATUS_CELL,
    content: <FormattedMessage id="environmentsStatusTourContent" />,
    dataTestId: "tour-environments-status"
  },
  {
    id: ENVIRONMENTS_TOUR_IDS.JIRA_CELL,
    target: ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS[ENVIRONMENT_JIRA_TICKETS_FIELD],
    content: <FormattedMessage id="environmentsJiraTicketsTourContent" />,
    dataTestId: "tour-environments-jira-tickets-tour-content"
  },
  {
    id: ENVIRONMENTS_TOUR_IDS.SOFT_CELL,
    target: ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS[ENVIRONMENT_SOFTWARE_FIELD],
    content: (
      <FormattedMessage id="environmentsSoftwareTourContent" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
    ),
    dataTestId: "tour-environments-software-tour-content"
  }
];

export const PRODUCT_TOUR_IDS = {
  HOME: "home",
  ENVIRONMENTS: "environments",
  RECOMMENDATIONS: "recommendations",
  RESOURCES: "resources",
  DATA_SOURCES: "dataSources",
  POOLS: "pools",
  USERS: "userManagement"
};

const PRODUCT_TOUR_STEPS = [
  {
    id: PRODUCT_TOUR_IDS.HOME,
    content: <FormattedMessage id="homeProductTourContent" />,
    dataTestId: "p_tour_home",
    target: PRODUCT_TOUR_IDS.HOME
  },
  {
    id: PRODUCT_TOUR_IDS.ENVIRONMENTS,
    content: <FormattedMessage id="environmentsProductTourContent" />,
    dataTestId: "p_tour_environments",
    target: PRODUCT_TOUR_IDS.ENVIRONMENTS
  },
  {
    id: PRODUCT_TOUR_IDS.RECOMMENDATIONS,
    content: <FormattedMessage id="recommendationsProductTourContent" />,
    dataTestId: "p_tour_recommendations",
    target: PRODUCT_TOUR_IDS.RECOMMENDATIONS
  },
  {
    id: PRODUCT_TOUR_IDS.RESOURCES,
    content: <FormattedMessage id="resourcesProductTourContent" />,
    dataTestId: "p_tour_resources",
    target: PRODUCT_TOUR_IDS.RESOURCES
  },
  {
    id: PRODUCT_TOUR_IDS.DATA_SOURCES,
    content: <FormattedMessage id="dataSourcesProductTourContent" />,
    dataTestId: "p_tour_data_source",
    target: PRODUCT_TOUR_IDS.DATA_SOURCES
  },
  {
    id: PRODUCT_TOUR_IDS.POOLS,
    content: <FormattedMessage id="poolsProductTourContent" />,
    dataTestId: "p_tour_pools",
    target: PRODUCT_TOUR_IDS.POOLS
  },
  {
    id: PRODUCT_TOUR_IDS.USERS,
    content: <FormattedMessage id="userManagementProductTourContent" />,
    dataTestId: "p_tour_user_management",
    target: PRODUCT_TOUR_IDS.USERS
  }
];

export const TOURS_DEFINITIONS = Object.freeze({
  [ENVIRONMENTS_TOUR]: ENVIRONMENTS_TOUR_STEPS,
  [PRODUCT_TOUR]: PRODUCT_TOUR_STEPS
});
