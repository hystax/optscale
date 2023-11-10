import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import { MlRunStatusIcon } from "components/MlRunStatus";

const StatusDescription = ({ messageId, icon }) => (
  <div
    style={{
      display: "inline-flex"
    }}
  >
    {icon}
    <span
      style={{
        paddingTop: "2px"
      }}
    >
      <FormattedMessage
        id={messageId}
        values={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    </span>
  </div>
);

const MlRunStatusHeaderCell = () => (
  <HeaderHelperCell
    titleMessageId="status"
    titleDataTestId="lbl_status"
    helperMessageId="statusTooltip"
    helperMessageValues={{
      running: <StatusDescription icon={<MlRunStatusIcon status="running" />} messageId="runningStatusDescription" />,
      aborted: <StatusDescription icon={<MlRunStatusIcon status="aborted" />} messageId="abortedStatusDescription" />,
      completed: <StatusDescription icon={<MlRunStatusIcon status="completed" />} messageId="completedStatusDescription" />,
      failed: <StatusDescription icon={<MlRunStatusIcon status="failed" />} messageId="failedStatusDescription" />,
      br: <br />
    }}
    onTooltipTitleClick={(e) => {
      // Prevent triggering sorting when clicking on the tooltip area
      e.stopPropagation();
    }}
  />
);

export default MlRunStatusHeaderCell;
