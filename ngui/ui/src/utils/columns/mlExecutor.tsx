import LoupeIcon from "@mui/icons-material/Loupe";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconButton from "components/IconButton";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";

const ExecutorInfo = ({ info, showRunInspect }) => {
  const { name, id, cloud_type: cloudType, cloud_resource_id: cloudResourceId, run, last_run: lastRun } = info;
  const timeAgo = useIntervalTimeAgo(lastRun, 1);

  const runInfo = run
    ? [
        {
          key: "model",
          node: (
            <div style={{ display: "flex", flexDirection: "row" }}>
              <KeyValueLabel keyMessageId="model" value={run} />
              {showRunInspect && (
                <Tooltip title={<FormattedMessage id="inspect" />}>
                  <IconButton icon={<LoupeIcon fontSize="inherit" />} />
                </Tooltip>
              )}
            </div>
          )
        },
        {
          key: "time",
          node: <KeyValueLabel keyMessageId="lastRun" value={timeAgo} />
        }
      ]
    : [];

  return (
    <CaptionedCell
      caption={[
        {
          key: "name",
          node: <KeyValueLabel keyMessageId="name" value={name} />
        },
        ...runInfo
      ]}
    >
      <IconLabel
        icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
        label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
      />
    </CaptionedCell>
  );
};

const mlExecutor = ({ headerDataTestId = "lbl_executor", showRunInspect = false } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="executor" />
    </TextWithDataTestId>
  ),
  id: "resource",
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({ row: { original } }) => <ExecutorInfo info={original} showRunInspect={showRunInspect} />
});

export default mlExecutor;
