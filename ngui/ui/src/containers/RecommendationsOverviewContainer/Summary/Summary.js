import React from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import SummaryGrid from "components/SummaryGrid";
import { useIsRiSpEnabled } from "hooks/useIsRiSpEnabled";
import { getRiSpCoverageUrl } from "urls";
import { SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { getCurrentUTCTimeInSec, getLast30DaysRange, getTimeDistance } from "utils/datetime";
import { getQueryParams } from "utils/network";

const getNextCheckCardValue = (lastRun, lastCompleted, nextRun) => {
  if (lastRun !== lastCompleted) {
    return {
      id: "runningRightNow"
    };
  }

  if (!nextRun) {
    return { id: "never" };
  }

  if (nextRun <= getCurrentUTCTimeInSec()) {
    return { id: "aboutToStart" };
  }

  return {
    id: "valueIn",
    values: {
      value: getTimeDistance(nextRun)
    }
  };
};

const getRiSpExpensesCardDefinition = ({ riSpExpensesSummary, isLoading, navigate }) => {
  const { totalCostWithOffer, totalSaving, computeExpensesCoveredWithCommitments } = riSpExpensesSummary;

  const getColor = () => {
    if (computeExpensesCoveredWithCommitments < 0.05) {
      return "error";
    }
    if (computeExpensesCoveredWithCommitments < 0.5) {
      return "warning";
    }

    return "success";
  };

  return {
    key: "riSpExpenses",
    type: SUMMARY_CARD_TYPES.EXTENDED,
    valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
    valueComponentProps: {
      value: totalSaving
    },
    color: getColor(),
    captionMessageId: "savedWithCommitmentsForTheLast30Days",
    dataTestIds: {
      cardTestId: "card_ri_sp_expenses",
      titleTestId: "p_ri_sp_expenses",
      valueTestId: "p_ri_sp_expenses"
    },
    relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,

    relativeValueComponentProps: {
      format: "percentage",
      value: computeExpensesCoveredWithCommitments
    },
    button: {
      show: true,
      icon: <ExitToAppOutlinedIcon />,
      onClick: () => {
        const { startDate, endDate } = getLast30DaysRange();
        const { dataSourceId } = getQueryParams();

        const url = getRiSpCoverageUrl({
          secondsStartDate: startDate,
          secondsEndDate: endDate,
          dataSourceId
        });

        navigate(url);
      },
      tooltip: {
        show: true,
        messageId: "seeRiSpCoverage",
        placement: "top"
      }
    },
    relativeValueCaptionMessageId: "computeExpensesCoveredWithCommitments",
    isLoading,
    renderCondition: () => totalCostWithOffer && totalCostWithOffer !== 0
  };
};

const Summary = ({ totalSaving, lastCompleted, lastRun, nextRun, riSpExpensesSummary, isLoadingProps }) => {
  const navigate = useNavigate();

  const isRiSpEnabled = useIsRiSpEnabled();

  const { isRecommendationsLoading, isRiSpExpensesSummaryLoading } = isLoadingProps;

  const summaryData = [
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
      },
      dataTestIds: {
        cardTestId: "card_saving",
        titleTestId: "p_saving",
        valueTestId: "p_saving_value"
      },
      captionMessageId: "possibleMonthlySavings",
      isLoading: isRecommendationsLoading
    },
    {
      key: "lastCheckTime",
      type: SUMMARY_CARD_TYPES.EXTENDED,
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
      valueComponentProps: {
        id: !lastCompleted ? "never" : "valueAgo",
        values: {
          value: !lastCompleted ? null : getTimeDistance(lastCompleted)
        }
      },
      captionMessageId: "lastCheckTime",
      dataTestIds: {
        cardTestId: "card_last_check",
        titleTestId: "p_last_check",
        valueTestId: "p_last_time"
      },
      relativeValueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
      relativeValueComponentProps: getNextCheckCardValue(lastRun, lastCompleted, nextRun),
      relativeValueCaptionMessageId: "nextCheckTime",
      isLoading: isRecommendationsLoading
    },
    ...(isRiSpEnabled
      ? [getRiSpExpensesCardDefinition({ riSpExpensesSummary, isLoading: isRiSpExpensesSummaryLoading, navigate })]
      : [])
  ];

  return <SummaryGrid summaryData={summaryData} />;
};

Summary.propTypes = {
  totalSaving: PropTypes.number,
  lastCompleted: PropTypes.number,
  lastRun: PropTypes.number,
  nextRun: PropTypes.number,
  isLoadingProps: PropTypes.object,
  riSpExpensesSummary: PropTypes.object
};

export default Summary;
