import React from "react";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import AlertDialog from "components/AlertDialog";
import DashboardGridLayout from "components/DashboardGridLayout";
import MailTo from "components/MailTo";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import PageContentWrapper from "components/PageContentWrapper";
import { PRODUCT_TOUR, useProductTour, useStartTour } from "components/Tour";
import EnvironmentsCardContainer from "containers/EnvironmentsCardContainer";
import OrganizationExpensesContainer from "containers/OrganizationExpensesContainer";
import RecommendationsCardContainer from "containers/RecommendationsCardContainer";
import TopResourcesExpensesCardContainer from "containers/TopResourcesExpensesCardContainer";
import { useApiData } from "hooks/useApiData";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { EMAIL_SUPPORT, DOCS_HYSTAX_OPTSCALE, SHOW_POLICY_QUERY_PARAM } from "urls";
import { ENVIRONMENT } from "utils/constants";
import { getQueryParams, removeQueryParam } from "utils/network";
import DashboardMocked from "./DashboardMocked";

const Dashboard = () => {
  const isUpMd = useIsUpMediaQuery("md");

  const startTour = useStartTour();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const thereAreOnlyEnvironmentDataSources = cloudAccounts.every(({ type }) => type === ENVIRONMENT);

  const { isFinished } = useProductTour(PRODUCT_TOUR);

  const { showPolicy } = getQueryParams();
  const firstTimeOpen = !!showPolicy;

  const closeAlert = (queryParams) => {
    removeQueryParam(queryParams);
    // TODO: https://datatrendstech.atlassian.net/browse/NGUI-2808 to handle dynamic header buttons, product tour is hidden on mdDown (when hamburger menu is activated)
    if (!isFinished && isUpMd) {
      startTour(PRODUCT_TOUR);
    }
  };

  const dashboardGridItems = {
    topResourcesExpensesCard: thereAreOnlyEnvironmentDataSources ? null : <TopResourcesExpensesCardContainer />,
    environmentsCard: <EnvironmentsCardContainer />,
    organizationExpenses: thereAreOnlyEnvironmentDataSources ? null : <OrganizationExpensesContainer />,
    recommendationsCard: <RecommendationsCardContainer />
  };

  return (
    <>
      <Mocked mock={<DashboardMocked />} backdropMessageType={MESSAGE_TYPES.DASHBOARD}>
        <PageContentWrapper>
          <DashboardGridLayout {...dashboardGridItems} />
        </PageContentWrapper>
      </Mocked>
      <AlertDialog
        show={firstTimeOpen}
        dataTestIds={{
          title: "lbl_privacy_policy",
          paper: "window_privacy_policy",
          button: "btn_proceed"
        }}
        header={<FormattedMessage id="optScalePrivacyPolicy" />}
        message={
          <FormattedMessage
            id="privacyWarning"
            values={{
              email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} />,
              docs: (chunks) => (
                <Link target="_blank" href={DOCS_HYSTAX_OPTSCALE} data-test-id="link_documentation">
                  {chunks}
                </Link>
              ),
              p: (chunks) => <p>{chunks}</p>,
              ul: (chunks) => <ul style={{ marginTop: 0 }}>{chunks}</ul>,
              li: (chunks) => <li>{chunks}</li>,
              strong: (chunks) => <strong>{chunks}</strong>,
              br: <br />
            }}
          />
        }
        buttonMessageId="proceedToOptScale"
        onClose={() => closeAlert(SHOW_POLICY_QUERY_PARAM)}
      />
    </>
  );
};

export default Dashboard;
