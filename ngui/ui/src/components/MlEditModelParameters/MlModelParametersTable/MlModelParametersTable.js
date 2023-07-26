import React, { useMemo } from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ML_MODELS_PARAMETERS } from "urls";
import { tendency, text } from "utils/columns";
import aggregateFunction from "utils/columns/aggregateFunction";

const tableActionBar = {
  show: true,
  definition: {
    items: [
      {
        key: "manageParametersLibrary",
        dataTestId: "btn_manage_global_parameters",
        icon: <SettingsIcon />,
        messageId: "manageParametersLibrary",
        variant: "text",
        type: "button",
        link: ML_MODELS_PARAMETERS
      }
    ]
  }
};

const MlModelParametersTable = ({ parameters, onAttachChange, isLoading }) => {
  const { isDemo } = useOrganizationInfo();

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
          <Tooltip title={isDemo ? <FormattedMessage id="notAvailableInLiveDemo" /> : undefined}>
            <div>
              <Switch
                disabled={isDemo}
                onChange={(event) => {
                  const action = event.target.checked ? "attach" : "detach";

                  onAttachChange({
                    [action]: [original.id]
                  });
                }}
                checked={original.is_attached}
              />
            </div>
          </Tooltip>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({ cell }) => <Typography>{cell.getValue()}</Typography>
      },
      text({ headerMessageId: "key", headerDataTestId: "lbl_key", accessorKey: "key", copy: true }),
      tendency(),
      aggregateFunction(),
      {
        header: (
          <TextWithDataTestId dataTestId="goal_value_lbl">
            <FormattedMessage id="goalValue" />
          </TextWithDataTestId>
        ),
        accessorKey: "target_value"
      }
    ],
    [isDemo, onAttachChange]
  );

  return (
    <Table
      withSearch
      actionBar={tableActionBar}
      isLoading={isLoading}
      data={parameters}
      columns={columns}
      localization={{
        emptyMessageId: "noParameters"
      }}
      pageSize={50}
    />
  );
};

MlModelParametersTable.propTypes = {
  parameters: PropTypes.array.isRequired,
  onAttachChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default MlModelParametersTable;
