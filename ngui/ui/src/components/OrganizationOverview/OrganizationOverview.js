import React, { useEffect, useRef } from "react";
import ArrowUpwardOutlinedIcon from "@mui/icons-material/ArrowUpwardOutlined";
import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import { Link } from "@mui/material";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import PoolsTable from "components/PoolsTable";
import PoolTypeIcon from "components/PoolTypeIcon";
import SummaryGrid from "components/SummaryGrid";
import TabsWrapper from "components/TabsWrapper";
import GetAssignmentRulesContainer from "containers/GetAssignmentRulesContainer";
import PoolConstraintsContainer from "containers/PoolConstraintsContainer";
import {
  ASSIGNMENT_RULES,
  getEditPoolUrl,
  getPoolUrl,
  getThisMonthPoolExpensesUrl,
  getResourcesExpensesUrl,
  getThisMonthResourcesByPoolUrl,
  getPoolIdWithSubPools,
  POOLS
} from "urls";
import {
  SUMMARY_VALUE_COMPONENT_TYPES,
  POOL_ID_FILTER,
  AVAILABLE_SAVINGS_FILTER,
  ORGANIZATION_OVERVIEW_TABS
} from "utils/constants";
import { getCurrentMonthRange } from "utils/datetime";
import { SPACING_2, getPoolColorStatus } from "utils/layouts";
import { intPercentXofY } from "utils/math";

const OrganizationOverview = ({ isLoadingProps = {}, pool }) => {
  const {
    id,
    name,
    limit = 0,
    cost = 0,
    forecast = 0,
    parent_id: parentId,
    unallocated_limit: unallocatedLimit = 0,
    saving = 0,
    default_owner_name: defaultResourceOwner,
    purpose: type
  } = pool;

  const { isGetPoolLoading = false, isGetPoolAllowedActionsLoading = false, isGetPoolDataReady = false } = isLoadingProps;

  // after get_pool should invoke drop container will load reload it
  // so "isGetPoolLoading" used for TabsWrapper isLoading will unmount side modal
  // that's why using ref
  const isPoolsDataInited = useRef(isGetPoolDataReady);
  useEffect(() => {
    isPoolsDataInited.current = isPoolsDataInited.current || isGetPoolDataReady;
  }, [isGetPoolDataReady]);

  const { today, startOfMonth } = getCurrentMonthRange(true);

  const baseActionBarItems = [
    {
      key: "goToParentPool",
      icon: <ArrowUpwardOutlinedIcon fontSize="small" />,
      messageId: "goToParentPool",
      type: "button",
      link: getPoolUrl(parentId),
      isLoading: isGetPoolLoading,
      show: !!parentId,
      dataTestId: "btn_parent"
    },
    {
      key: "edit",
      icon: <EditOutlinedIcon fontSize="small" />,
      messageId: "edit",
      link: getEditPoolUrl(id),
      type: "button",
      isLoading: isGetPoolLoading || isGetPoolAllowedActionsLoading,
      requiredActions: ["MANAGE_POOLS"],
      dataTestId: "btn_edit"
    },
    {
      key: "seeInCostExplorer",
      icon: <BarChartOutlinedIcon fontSize="small" />,
      messageId: "seeInCostExplorer",
      link: getThisMonthPoolExpensesUrl(id),
      isLoading: isGetPoolLoading,
      type: "button",
      dataTestId: "btn_see_in_ce"
    },
    {
      key: "seeResourceList",
      icon: <StorageOutlinedIcon fontSize="small" />,
      messageId: "seeResourceList",
      link: getThisMonthResourcesByPoolUrl(id),
      isLoading: isGetPoolLoading,
      type: "button",
      dataTestId: "btn_see_rl"
    },
    {
      key: "configureAssignmentRules",
      icon: <AssignmentOutlinedIcon fontSize="small" />,
      messageId: "configureAssignmentRules",
      link: ASSIGNMENT_RULES,
      isLoading: isGetPoolLoading,
      type: "button",
      dataTestId: "btn_configure_assignment_rules"
    }
  ];

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={POOLS} component={RouterLink}>
        <FormattedMessage id="pools" />
      </Link>
    ],
    title: {
      text: name,
      logo: {
        icon: <PoolTypeIcon fontSize="medium" type={type} hasRightMargin dataTestId="img_type" />
      },
      isLoading: isGetPoolLoading,
      dataTestId: "lbl_pool_name"
    },
    items: baseActionBarItems,
    poolId: id
  };

  const tabs = [
    {
      title: ORGANIZATION_OVERVIEW_TABS.POOLS,
      node: !!id && <PoolsTable rootPool={pool} isLoadingProps={{ isGetPoolLoading, isGetPoolAllowedActionsLoading }} />,
      dataTestId: "btn_tab_pools"
    },
    {
      title: ORGANIZATION_OVERVIEW_TABS.CONSTRAINTS,
      node: !!id && <PoolConstraintsContainer poolId={id} />,
      dataTestId: "btn_tab_constraints"
    },
    {
      title: ORGANIZATION_OVERVIEW_TABS.ASSIGNMENT_RULES,
      node: !!id && <GetAssignmentRulesContainer poolId={id} defaultResourceOwner={defaultResourceOwner} />,
      dataTestId: "btn_tab_rules"
    }
  ];

  const costPercent = intPercentXofY(cost, limit);
  const forecastPercent = intPercentXofY(forecast, limit);

  const summaryDefinition = [
    {
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: limit
      },
      captionMessageId: "poolLimit",
      key: "pool",
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_pool"
      }
    },
    {
      key: "expensesThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: cost
      },
      color: getPoolColorStatus(costPercent),
      captionMessageId: "expensesThisMonth",
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_expenses"
      }
    },
    {
      key: "forecastThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: forecast
      },
      captionMessageId: "forecastThisMonth",
      color: getPoolColorStatus(forecastPercent),
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_forecast"
      }
    },
    {
      key: "unallocatedPool",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: unallocatedLimit
      },
      captionMessageId: "unallocatedPoolBudget",
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_unallocated"
      }
    },
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: saving
      },
      captionMessageId: "possibleMonthlySavings",
      renderCondition: () => saving !== 0,
      button: {
        show: true,
        icon: <ListAltOutlinedIcon />,
        link: getResourcesExpensesUrl({
          [POOL_ID_FILTER]: getPoolIdWithSubPools(id),
          [AVAILABLE_SAVINGS_FILTER]: true,
          sStartDate: startOfMonth,
          sEndDate: today
        }),
        tooltip: {
          show: true,
          messageId: "goToResources",
          placement: "top"
        }
      },
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_savings"
      }
    },
    {
      key: "defaultResourceOwner",
      value: defaultResourceOwner,
      captionMessageId: "defaultResourceOwner",
      renderCondition: () => !!defaultResourceOwner,
      isLoading: isGetPoolLoading,
      dataTestIds: {
        cardTestId: "card_owner"
      }
    }
  ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item>
            <SummaryGrid summaryData={summaryDefinition} />
          </Grid>
          <Grid item xs={12}>
            <TabsWrapper
              isLoading={!isPoolsDataInited.current}
              tabsProps={{
                tabs,
                defaultTab: ORGANIZATION_OVERVIEW_TABS.POOLS,
                name: "organization-overview"
              }}
            />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

OrganizationOverview.propTypes = {
  pool: PropTypes.object.isRequired,
  isLoadingProps: PropTypes.object
};

export default OrganizationOverview;
