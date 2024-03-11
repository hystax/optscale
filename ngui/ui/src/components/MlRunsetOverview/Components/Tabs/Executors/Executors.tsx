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
import { expenses, resourceLocation } from "utils/columns";
import { getCloudResourceIdentifier } from "utils/resources";
import { CELL_EMPTY_VALUE } from "utils/tables";

const STATUSES = Object.freeze({
  STARTING_PREPARING: "starting preparing",
  STARTING: "starting",
  STARTED: "started",
  DESTROYING_SCHEDULED: "destroying scheduled",
  DESTROY_PREPARING: "destroy preparing",
  DESTROYING: "destroying",
  DESTROYED: "destroyed",
  ERROR: "error",
  WAITING_ARCEE: "waiting arcee",
  UNKNOWN: "unknown"
});

const Executors = ({ executors, isLoading }) => {
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
            original: { reason: errorReason }
          }
        }) => {
          const status = cell.getValue();

          const getStatusTranslationId = () =>
            ({
              [STATUSES.STARTING_PREPARING]: "startPreparing",
              [STATUSES.STARTING]: "starting",
              [STATUSES.STARTED]: "started",
              [STATUSES.DESTROYING_SCHEDULED]: "terminateScheduled",
              [STATUSES.DESTROY_PREPARING]: "terminatePrepared",
              [STATUSES.DESTROYING]: "terminating",
              [STATUSES.DESTROYED]: "terminated",
              [STATUSES.ERROR]: "error",
              [STATUSES.WAITING_ARCEE]: "waitingOptscaleArcee",
              [STATUSES.UNKNOWN]: "unknown"
            })[status];

          const translationId = getStatusTranslationId();

          return translationId ? (
            <CaptionedCell caption={status === STATUSES.ERROR ? errorReason : undefined}>
              <FormattedMessage id={translationId} />
            </CaptionedCell>
          ) : (
            CELL_EMPTY_VALUE
          );
        }
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
              ip_addr: ipAddress
            }
          }
        }) => {
          const cloudResourceIdentifier = getCloudResourceIdentifier({
            cloud_resource_id: instanceId
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
                  show: name !== cloudResourceIdentifier
                },
                {
                  key: "instance_size",
                  node: (
                    <KeyValueLabel
                      variant="caption"
                      keyMessageId="size"
                      value={<CloudLabel name={<strong>{instanceName}</strong>} type={instanceCloudType} disableLink />}
                    />
                  )
                },
                {
                  key: "ip",
                  node: <KeyValueLabel variant="caption" keyMessageId="ip" value={ipAddress} />
                }
              ]}
            >
              <ResourceLabel cloudResourceIdentifier={cloudResourceIdentifier} />
            </CaptionedCell>
          );
        }
      },
      resourceLocation({
        headerDataTestId: "lbl_location",
        idAccessor: "cloud_id",
        typeAccessor: "cloud_type",
        locationAccessors: {
          region: "region_name"
        },
        accessorKey: "cloud_name"
      }),
      expenses({
        id: "expenses",
        headerDataTestId: "lbl_expenses",
        headerMessageId: "expenses",
        accessorKey: "cost"
      })
    ],
    []
  );

  const tableData = useMemo(
    () =>
      executors.map((executor) => ({
        ...executor,
        cloud_id: executor.cloud_account?.id ?? "",
        cloud_type: executor.cloud_account?.type ?? "",
        region_name: executor.region?.name ?? "",
        cloud_name: executor.cloud_account?.name ?? ""
      })),
    [executors]
  );

  return isLoading ? (
    <TableLoader columnsCounter={4} />
  ) : (
    <Table data={tableData} columns={columns} localization={{ emptyMessageId: "noExecutors" }} pageSize={50} />
  );
};

export default Executors;
