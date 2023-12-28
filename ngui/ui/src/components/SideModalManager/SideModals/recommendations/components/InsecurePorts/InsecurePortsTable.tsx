import { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
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
        header: <FormattedMessage id="port" />,
        accessorKey: "portString",
        style: {
          minWidth: 400
        },
        defaultSort: "asc",
        enableHiding: false
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        enableHiding: false,
        cell: ({ row: { original: { id, protocol, port } = {}, index } }) => (
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
      enablePaginationQueryParam={false}
      withSearch
      enableSearchQueryParam={false}
      counters={{ showCounters: true, hideDisplayed: true }}
      localization={{
        emptyMessageId: "noPorts"
      }}
    />
  );
};

export default InsecurePortsTable;
