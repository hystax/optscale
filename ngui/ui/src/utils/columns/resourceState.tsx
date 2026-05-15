import CircleIcon from "@mui/icons-material/Circle";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";

type ResourceStateValue = string | boolean | null | undefined;

const RUNNING_STATES = new Set(["running", "available", "started", "active"]);
const STOPPED_STATES = new Set(["stopped", "paused", "terminated", "terminated_with_errors"]);

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

const getState = (stoppedAllocated: ResourceStateValue) => {
  if (stoppedAllocated === true) {
    return { messageId: "stopped", color: "error" as const };
  }
  if (stoppedAllocated === false) {
    return { messageId: "running", color: "success" as const };
  }
  if (typeof stoppedAllocated === "string") {
    const lower = stoppedAllocated.toLowerCase();
    if (RUNNING_STATES.has(lower)) {
      return { messageId: "running", color: "success" as const };
    }
    if (STOPPED_STATES.has(lower)) {
      return { messageId: "stopped", color: "error" as const };
    }
    return { messageId: lower, color: "warning" as const };
  }
  return { messageId: "unknown", color: "disabled" as const };
};

const resourceState = ({
  headerDataTestId = "lbl_resource_state",
  accessorKey = "stopped_allocated",
  accessorFn = undefined as ((row: unknown) => ResourceStateValue) | undefined,
} = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="state" />
    </TextWithDataTestId>
  ),
  ...(accessorFn ? { id: accessorKey, accessorFn } : { accessorKey }),
  cell: ({ cell }) => {
    const value = cell.getValue() as ResourceStateValue;
    const { messageId, color } = getState(value);
    const label = <FormattedMessage id={messageId} defaultMessage={capitalize(messageId)} />;
    return (
      <Tooltip title={label}>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <CircleIcon fontSize="small" color={color} sx={{ fontSize: 10 }} />
          {label}
        </span>
      </Tooltip>
    );
  },
});

export default resourceState;
