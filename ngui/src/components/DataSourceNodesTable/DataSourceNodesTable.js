import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import CostModelFormattedMoney from "components/CostModelFormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { unixTimestampToDateTime } from "utils/datetime";

const useDataSourceNodesTableData = (nodes) => {
  const intl = useIntl();
  return useMemo(() => {
    const cpuCapacityString = intl.formatMessage({ id: "cpu" });
    const memoryCapacityString = intl.formatMessage({ id: "memory" });

    const getFlavorCapacityString = ({ cpu, memory }) => {
      const cpuSubstring = `${cpuCapacityString}: ${cpu}`;
      const memorySubstring = `${memoryCapacityString}: ${memory}`;
      return [cpuSubstring, memorySubstring].join(" ");
    };

    const getFlavorInfoString = (flavorName, capacity) => {
      const capacityString = getFlavorCapacityString(capacity);
      return flavorName ? [flavorName, capacityString].join(" ") : capacityString;
    };

    const getFlavorInfoCell = ({ flavor: flavorName = "", cpu = 0, memory = 0 }) => {
      // «undefined» means default
      const capacityLabelVariant = flavorName ? "caption" : undefined;

      return {
        getStringRepresentation: () => getFlavorInfoString(flavorName, { cpu, memory }),
        render: () => (
          <CaptionedCell
            caption={[
              {
                key: "cpu",
                node: <KeyValueLabel text={cpuCapacityString} value={cpu} variant={capacityLabelVariant} />
              },
              {
                key: "memory",
                node: (
                  <KeyValueLabel
                    text={memoryCapacityString}
                    value={`${memory} ${intl.formatMessage({ id: "GB" })}`}
                    variant={capacityLabelVariant}
                  />
                )
              }
            ]}
          >
            {flavorName}
          </CaptionedCell>
        )
      };
    };

    const addFlavorInfoToNode = (node) => {
      const { getStringRepresentation: getFlavorInfoStringRepresentation, render: renderFlavorInfoCell } =
        getFlavorInfoCell(node);

      return {
        ...node,
        flavorInfoString: getFlavorInfoStringRepresentation(),
        renderFlavorInfoCell
      };
    };

    return nodes.map(addFlavorInfoToNode);
  }, [intl, nodes]);
};

const DataSourceNodesTable = ({ nodes, actionBar, isLoading = false }) => {
  const nodeTableColumns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_node_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessor: "name",
        Cell: ({
          cell: { value },
          row: {
            original: { provider }
          }
        }) => <CloudLabel label={value} type={provider} />
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_node_flavor">
            <FormattedMessage id="size" />
          </TextWithDataTestId>
        ),
        accessor: "flavorInfoString",
        Cell: ({ row: { original } }) => original.renderFlavorInfoCell()
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_node_hourly_price">
            <FormattedMessage id="hourlyPrice" />
          </TextWithDataTestId>
        ),
        accessor: "hourly_price",
        Cell: ({ cell: { value } }) => <CostModelFormattedMoney value={value} />,
        defaultSort: "desc"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_node_last_seen">
            <FormattedMessage id="lastSeenOn" />
          </TextWithDataTestId>
        ),
        accessor: "last_seen",
        Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
      }
    ],
    []
  );

  const tableData = useDataSourceNodesTableData(nodes);

  return isLoading ? (
    <TableLoader columnsCounter={nodeTableColumns.length} />
  ) : (
    <Table
      data={tableData}
      columns={nodeTableColumns}
      localization={{
        emptyMessageId: "noNodes"
      }}
      actionBar={actionBar}
    />
  );
};

DataSourceNodesTable.propTypes = {
  nodes: PropTypes.array.isRequired,
  actionBar: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default DataSourceNodesTable;
