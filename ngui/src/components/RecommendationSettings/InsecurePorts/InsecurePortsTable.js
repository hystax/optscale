import React, { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatProtocolPortAppLabel } from "hooks/useFormatProtocolPortAppLabel";

const InsecurePortsTable = ({ ports, portsMap, onDelete, isLoading = false }) => {
  const formatProtocolPortAppLabel = useFormatProtocolPortAppLabel();
  const memoizedPorts = useMemo(
    () =>
      ports.map((port) => ({
        portString: formatProtocolPortAppLabel({
          port: port.port,
          protocol: port.protocol,
          app: portsMap[port.port]
        }),
        ...port
      })),

    [formatProtocolPortAppLabel, ports, portsMap]
  );

  const columns = useMemo(
    () => [
      {
        Header: <FormattedMessage id="port" />,
        accessor: "portString",
        style: {
          minWidth: 400
        },
        defaultSort: "asc",
        isStatic: true
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        disableSortBy: true,
        isStatic: true,
        Cell: ({ row: { original: { id, protocol, port } = {}, index } }) => (
          <TableCellActions
            entityId={id}
            items={[
              {
                key: "delete",
                messageId: "delete",
                icon: <DeleteOutlinedIcon />,
                color: "error",
                requiredActions: ["MANAGE_RESOURCES"],
                dataTestId: `btn_delete_${index}`,
                action: () => onDelete(protocol, port)
              }
            ]}
          />
        )
      }
    ],
    [onDelete]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} />
  ) : (
    <Table
      data={memoizedPorts}
      columns={columns}
      pageSize={50}
      withSearch
      counters={{ showCounters: true, hideDisplayed: true }}
      localization={{
        emptyMessageId: "noPorts"
      }}
      queryParamPrefix="ports"
      autoResetSortBy={false}
    />
  );
};

InsecurePortsTable.propTypes = {
  ports: PropTypes.array.isRequired,
  portsMap: PropTypes.object.isRequired,
  onDelete: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default InsecurePortsTable;
