import React from "react";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import AlertDialog from "components/AlertDialog";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import DashboardGridLayout from "components/DashboardGridLayout";
import MailTo from "components/MailTo";
import Mocked from "components/Mocked";
import PageContentWrapper from "components/PageContentWrapper";
import { startTour, PRODUCT_TOUR, TOURS } from "components/ProductTour";
import EnvironmentsCardContainer from "containers/EnvironmentsCardContainer";
import MyTasksContainer from "containers/MyTasksContainer";
import OrganizationExpensesContainer from "containers/OrganizationExpensesContainer";
import RecommendationsCardContainer from "containers/RecommendationsCardContainer";
import TopResourcesExpensesCardContainer from "containers/TopResourcesExpensesCardContainer";
import { useApiData } from "hooks/useApiData";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { useRootData } from "hooks/useRootData";
import { EMAIL_SUPPORT, DOCS_HYSTAX_OPTSCALE, SHOW_POLICY_QUERY_PARAM } from "urls";
import { ENVIRONMENT } from "utils/constants";
import { getQueryParams, removeQueryParam } from "utils/network";
import DashboardMocked from "./DashboardMocked";

const Dashboard = () => {
  const isUpMd = useIsUpMediaQuery("md");

  const dispatch = useDispatch();

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const thereAreOnlyEnvironmentDataSources = cloudAccounts.every(({ type }) => type === ENVIRONMENT);

  const { rootData: { [PRODUCT_TOUR]: { isFinished } = {} } = {} } = useRootData(TOURS);

  const { showPolicy } = getQueryParams();
  const firstTimeOpen = !!showPolicy;

  const closeAlert = (queryParams) => {
    removeQueryParam(queryParams);
    // TODO: https://datatrendstech.atlassian.net/browse/NGUI-2808 to handle dynamic header buttons, product tour is hidden on mdDown (when hamburger menu is activated)
    if (!isFinished && isUpMd) {
      dispatch(startTour(PRODUCT_TOUR));
    }
  };

  const dashboardGridItems = {
    topResourcesExpensesCard: thereAreOnlyEnvironmentDataSources ? null : <TopResourcesExpensesCardContainer />,
    environmentsCard: <EnvironmentsCardContainer />,
    organizationExpenses: thereAreOnlyEnvironmentDataSources ? null : <OrganizationExpensesContainer />,
    recommendationsCard: <RecommendationsCardContainer />,
    myTasksCard: <MyTasksContainer />
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
