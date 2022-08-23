import React from "react";
import PowerOffOutlinedIcon from "@mui/icons-material/PowerOffOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import CloudInfo from "components/CloudInfo";
import PageContentWrapper from "components/PageContentWrapper";
import { DisconnectCloudAccountModal } from "components/SideModalManager/SideModals";
import SummaryGrid from "components/SummaryGrid";
import TabsWrapper from "components/TabsWrapper";
import DataSourceNodesContainer from "containers/DataSourceNodesContainer";
import UploadCloudReportDataContainer from "containers/UploadCloudReportDataContainer";
import { useDataSources } from "hooks/useDataSources";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  AWS_CNR,
  KUBERNETES_CNR,
  SUMMARY_VALUE_COMPONENT_TYPES,
  SUMMARY_CARD_TYPES,
  CLOUD_ACCOUNT_DETAILS_PAGE_TABS,
  ENVIRONMENT
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getPercentageChangeModule } from "utils/math";

const { DETAILS: DETAILS_TAB, UPLOAD: UPLOAD_TAB, NODES: NODES_TAB } = CLOUD_ACCOUNT_DETAILS_PAGE_TABS;

const CloudAccountDetails = ({ data, isLoading }) => {
  const openSideModal = useOpenSideModal();
  const { id, name = "", type, account_id: accountId, last_import_at: lastImportAt, details = {}, config } = data;
  const { isDemo } = useOrganizationInfo();

  const { cost = 0, last_month_cost: lastMonthCost = 0, forecast = 0 } = details;

  const tabs = [
    {
      title: DETAILS_TAB,
      dataTestId: "tab_details",
      node: !!id && <CloudInfo accountId={accountId} lastImportAt={lastImportAt} type={type} config={config} />
    },
    {
      title: UPLOAD_TAB,
      dataTestId: "tab_upload",
      node: !!id && <UploadCloudReportDataContainer cloudAccountId={id} />,
      renderCondition: () => type === AWS_CNR && !isDemo
    },
    {
      title: NODES_TAB,
      dataTestId: "tab_cost_model",
      node: !!id && <DataSourceNodesContainer cloudAccountId={id} costModel={config.cost_model} />,
      renderCondition: () => type === KUBERNETES_CNR
    }
  ];

  // TODO: initial values from useDataSources are default ones, which means logo is empty, Icon is null, JSX error in console.
  // Additional check on Icon mount below.
  // Loading state is inconsistent, the title is not displayed at all on initial load
  const {
    logo,
    icon: Icon,
    feType,
    dataTestIds: { img: imgDataTestId }
  } = useDataSources(type);

  const actionBarDefinition = {
    goBack: true,
    title: {
      text: name,
      dataTestId: "lbl_cloud_name",
      isLoading,
      logo: logo
        ? {
            src: logo,
            alt: feType,
            dataTestId: imgDataTestId
          }
        : { icon: Icon && <Icon /> }
    },
    items:
      isDemo || type === ENVIRONMENT
        ? []
        : [
            {
              key: "cloudAccountDetails-disconnect",
              icon: <PowerOffOutlinedIcon fontSize="small" />,
              messageId: "disconnect",
              dataTestId: "btn_open_disconnect_data_source_modal",
              type: "button",
              isLoading,
              action: () => openSideModal(DisconnectCloudAccountModal, { name, id, type }),
              requiredActions: ["MANAGE_CLOUD_CREDENTIALS"]
            }
          ]
  };

  const getSummaryData = () =>
    lastMonthCost
      ? [
          {
            key: "totalExpensesMonthToDate",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: cost
            },
            captionMessageId: "totalExpensesMonthToDate",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(cost, lastMonthCost) / 100,
              format: "percentage"
            },
            relativeValueCaptionMessageId: cost > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_total_exp"
            },
            color: cost > lastMonthCost ? "error" : "success",
            isLoading
          },
          {
            key: "forecastForThisMonth",
            type: SUMMARY_CARD_TYPES.EXTENDED,
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: forecast
            },
            captionMessageId: "forecastForThisMonth",
            relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
            relativeValueComponentProps: {
              value: getPercentageChangeModule(forecast, lastMonthCost) / 100,
              format: "percentage"
            },
            relativeValueCaptionMessageId: forecast > lastMonthCost ? "moreThanForPreviousMonth" : "lessThanForPreviousMonth",
            dataTestIds: {
              cardTestId: "card_forecast"
            },
            color: forecast > lastMonthCost ? "error" : "success",
            isLoading
          }
        ]
      : [
          {
            key: "totalExpensesMonthToDate",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: cost
            },
            captionMessageId: "totalExpensesMonthToDate",
            dataTestIds: {
              cardTestId: "card_total_exp"
            },
            isLoading
          },
          {
            key: "forecastForThisMonth",
            valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
            valueComponentProps: {
              value: forecast
            },
            captionMessageId: "forecastForThisMonth",
            dataTestIds: {
              cardTestId: "card_forecast"
            },
            isLoading
          }
        ];

  const renderDetails = () => (
    <>
      <Grid container spacing={SPACING_2}>
        <Grid item>
          <SummaryGrid summaryData={getSummaryData()} />
        </Grid>
        <Grid item xs={12}>
          <TabsWrapper
            wrapperCardDataTestIds={{ wrapper: "div_info" }}
            isLoading={isLoading}
            tabsProps={{
              tabs,
              defaultTab: DETAILS_TAB,
              name: "cloud-account"
            }}
          />
        </Grid>
      </Grid>
    </>
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>{renderDetails()}</PageContentWrapper>
    </>
  );
};

CloudAccountDetails.propTypes = {
  data: PropTypes.object,
  isLoading: PropTypes.bool
};

export default CloudAccountDetails;
