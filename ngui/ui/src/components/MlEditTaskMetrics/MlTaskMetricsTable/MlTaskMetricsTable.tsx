import { useMemo } from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { ML_METRICS } from "urls";
import { tendency, text } from "utils/columns";
import aggregateFunction from "utils/columns/aggregateFunction";

const tableActionBar = {
  show: true,
  definition: {
    items: [
      {
        key: "manageMetricsLibrary",
        dataTestId: "btn_manage_global_metrics",
        icon: <SettingsIcon />,
        messageId: "manageMetricsLibrary",
        variant: "text",
        type: "button",
        link: ML_METRICS,
      },
    ],
  },
};

const MlTaskMetricsTable = ({ metrics, onAttachChange, isLoading }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        cell: ({ row: { original } }) => (
          <Tooltip title={restrictionReasonMessage}>
            <div>
              <Switch
                disabled={isRestricted}
                onChange={(event) => {
                  const action = event.target.checked ? "attach" : "detach";

                  onAttachChange({
                    [action]: [original.id],
                  });
                }}
                checked={original.is_attached}
              />
            </div>
          </Tooltip>
        ),
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({ cell }) => <Typography>{cell.getValue()}</Typography>,
      },
      text({ headerMessageId: "key", headerDataTestId: "lbl_key", accessorKey: "key", copy: true }),
      tendency(),
      text({ headerMessageId: "unit", headerDataTestId: "lbl_unit", accessorKey: "unit" }),
      aggregateFunction(),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_target_value">
            <FormattedMessage id="targetValue" />
          </TextWithDataTestId>
        ),
        accessorKey: "target_value",
      },
    ],
    [isRestricted, onAttachChange, restrictionReasonMessage]
  );

  return (
    <Table
      withSearch
      actionBar={tableActionBar}
      isLoading={isLoading}
      data={metrics}
      columns={columns}
      localization={{
        emptyMessageId: "noMetrics",
      }}
      pageSize={50}
    />
  );
};

export default MlTaskMetricsTable;
