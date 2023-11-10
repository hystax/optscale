import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedDuration from "components/FormattedDuration";
import QuestionMark from "components/QuestionMark";
import { STATUS, getStatusColor } from "components/S3DuplicateFinderCheck/utils";
import SummaryGrid from "components/SummaryGrid";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";

const Status = ({ status, lastError }) => {
  if (status === STATUS.FAILED) {
    return (
      <Box display="flex" alignItems="center">
        <FormattedMessage id="failed" />
        <QuestionMark color="error" tooltipText={lastError} Icon={ErrorOutlineOutlinedIcon} />
      </Box>
    );
  }

  return (
    <FormattedMessage
      id={
        {
          [STATUS.SUCCESS]: "completed",
          [STATUS.RUNNING]: "running",
          [STATUS.CREATED]: "created",
          [STATUS.QUEUED]: "created"
        }[status] ?? "created"
      }
    />
  );
};

const Summary = ({
  status,
  duplicateSize,
  duplicateCount,
  lastRun,
  lastCompleted,
  monthlySavings,
  lastError,
  totalObjects,
  isLoading
}) => {
  const items = [
    {
      key: "status",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: Status,
      valueComponentProps: {
        status,
        lastError
      },
      color: getStatusColor(status),
      captionMessageId: "status",
      isLoading,
      dataTestIds: {
        cardTestId: "card_status"
      }
    },
    {
      key: "savings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: monthlySavings
      },
      captionMessageId: "savings",
      renderCondition: () => status === STATUS.SUCCESS,
      isLoading,
      dataTestIds: {
        cardTestId: "card_savings"
      }
    },
    {
      key: "objectsScanned",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
      valueComponentProps: {
        value: totalObjects
      },
      caption: <FormattedMessage id="scannedObjects" />,
      renderCondition: () => status === STATUS.SUCCESS,
      isLoading,
      dataTestIds: {
        cardTestId: "card_scanned_objects"
      }
    },
    {
      key: "size",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: FormattedDigitalUnit,
      valueComponentProps: { value: duplicateSize, baseUnit: SI_UNITS.BYTE },
      caption: <FormattedMessage id="inXDuplicateObjects" values={{ value: duplicateCount }} />,
      renderCondition: () => status === STATUS.SUCCESS,
      isLoading,
      dataTestIds: {
        cardTestId: "card_size"
      }
    },
    {
      key: "duration",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: FormattedDuration,
      valueComponentProps: {
        durationInSeconds: status === STATUS.RUNNING ? millisecondsToSeconds(+new Date()) - lastRun : lastCompleted - lastRun
      },
      captionMessageId: "duration",
      renderCondition: () => [STATUS.SUCCESS, STATUS.RUNNING].includes(status),
      isLoading,
      dataTestIds: {
        cardTestId: "card_duration"
      }
    }
  ];

  return <SummaryGrid summaryData={items} />;
};

export default Summary;
