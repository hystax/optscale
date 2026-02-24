import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import ResourceLabel from "components/ResourceLabel";
import ResourceName from "components/ResourceName";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsOptScaleCapabilityEnabled } from "hooks/useIsOptScaleCapabilityEnabled";
import { expenses, resourceLocation } from "utils/columns";
import { OPTSCALE_CAPABILITY } from "utils/constants";
import { getCloudResourceIdentifier } from "utils/resources";
import { CELL_EMPTY_VALUE } from "utils/tables";

const STATE = Object.freeze({
  STARTING_PREPARING: "starting preparing",
  STARTING: "starting",
  STARTED: "started",
  DESTROYING_SCHEDULED: "destroying scheduled",
  DESTROY_PREPARING: "destroy preparing",
  DESTROYING: "destroying",
  DESTROYED: "destroyed",
  ERROR: "error",
  WAITING_ARCEE: "waiting arcee",
  UNKNOWN: "unknown",
});

const STATE_TRANSLATION_MAP = Object.freeze({
  [STATE.STARTING_PREPARING]: "startPreparing",
  [STATE.STARTING]: "starting",
  [STATE.STARTED]: "started",
  [STATE.DESTROYING_SCHEDULED]: "terminateScheduled",
  [STATE.DESTROY_PREPARING]: "terminatePrepared",
  [STATE.DESTROYING]: "terminating",
  [STATE.DESTROYED]: "terminated",
  [STATE.ERROR]: "error",
  [STATE.WAITING_ARCEE]: "waitingOptscaleArcee",
  [STATE.UNKNOWN]: "unknown",
});

const Executors = ({ executors, isLoading }) => {
  const isFinOpsEnabled = useIsOptScaleCapabilityEnabled(OPTSCALE_CAPABILITY.FINOPS);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        accessorKey: "state",
        disableSortBy: true,
        cell: ({
          cell,
          row: {
            original: { reason },
          },
        }) => {
          const state = cell.getValue();

          const translationId = STATE_TRANSLATION_MAP[state];

          return translationId ? (
            <CaptionedCell caption={[STATE.ERROR, STATE.DESTROYED].includes(state) ? reason : undefined}>
              <FormattedMessage id={translationId} />
            </CaptionedCell>
          ) : (
            CELL_EMPTY_VALUE
          );
        },
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_instance">
            <FormattedMessage id="instance" />
          </TextWithDataTestId>
        ),
        accessorKey: "instance_id",
        cell: ({
          row: {
            original: {
              instance_id: instanceId,
              name = "",
              instance_size: { name: instanceName, cloud_type: instanceCloudType },
              ip_addr: ipAddress,
            },
          },
        }) => {
          const cloudResourceIdentifier = getCloudResourceIdentifier({
            cloud_resource_id: instanceId,
          });
          return (
            <CaptionedCell
              caption={[
                {
                  key: "resource_name",
                  node: (
                    <KeyValueLabel
                      variant="caption"
                      keyMessageId="name"
                      value={name ? <ResourceName name={name} /> : undefined}
                    />
                  ),
                  show: name !== cloudResourceIdentifier,
                },
                {
                  key: "instance_size",
                  node: (
                    <KeyValueLabel
                      variant="caption"
                      keyMessageId="size"
                      value={<CloudLabel name={<strong>{instanceName}</strong>} type={instanceCloudType} disableLink />}
                    />
                  ),
                },
                {
                  key: "ip",
                  node: <KeyValueLabel variant="caption" keyMessageId="ip" value={ipAddress} />,
                },
              ]}
            >
              <ResourceLabel cloudResourceIdentifier={cloudResourceIdentifier} />
            </CaptionedCell>
          );
        },
      },
      resourceLocation({
        headerDataTestId: "lbl_location",
        idAccessor: "cloud_id",
        typeAccessor: "cloud_type",
        locationAccessors: {
          region: "region_name",
        },
        accessorKey: "cloud_name",
      }),
      ...(isFinOpsEnabled
        ? [
            expenses({
              id: "expenses",
              headerDataTestId: "lbl_expenses",
              headerMessageId: "expenses",
              accessorKey: "cost",
            }),
          ]
        : []),
    ],
    [isFinOpsEnabled]
  );

  const tableData = useMemo(
    () =>
      executors.map((executor) => ({
        ...executor,
        cloud_id: executor.cloud_account?.id ?? "",
        cloud_type: executor.cloud_account?.type ?? "",
        region_name: executor.region?.name ?? "",
        cloud_name: executor.cloud_account?.name ?? "",
      })),
    [executors]
  );

  return isLoading ? (
    <TableLoader columnsCounter={4} />
  ) : (
    <Table
      data={tableData}
      columns={columns}
      localization={{ emptyMessageId: "noExecutors" }}
      pageSize={50}
      queryParamPrefix="executors"
    />
  );
};

export default Executors;
