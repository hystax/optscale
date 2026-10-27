import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { useParams } from "react-router-dom";
import { AddInstanceToScheduleModal, RemoveInstancesFromScheduleModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { isEmptyArray } from "utils/arrays";
import { powerScheduleInstance, resourceLocation, resourcePoolOwner, size, tags } from "utils/columns";

type PowerScheduleInstance = {
  id: string;
  cloud_resource_id: string;
  name: string;
  pool_id: string;
  pool_name: string;
  pool_purpose: string;
  details: {
    owner_name: string;
    pool_name: string;
    pool_purpose: string;
    region: string;
    cloud_name: string;
    cloud_type: string;
  };
  cloud_account_id: string;
  meta: {
    flavor: string;
  };
  tags: Record<string, string>;
};

type PowerScheduleInstancesProps = {
  instances: PowerScheduleInstance[];
};

const PowerScheduleInstances = ({ instances }: PowerScheduleInstancesProps) => {
  const { powerScheduleId } = useParams();

  const openSideModal = useOpenSideModal();

  const tableData = useMemo(
    () =>
      instances.map((instance) => ({
        id: instance.id,
        active: instance.active,
        cloud_resource_id: instance.cloud_resource_id,
        name: instance.name,
        owner_name: instance.details?.owner_name,
        pool_id: instance.pool_id,
        pool_name: instance.details?.pool_name,
        pool_purpose: instance.details?.pool_purpose,
        region: instance.details?.region,
        cloud_account_id: instance.cloud_account_id,
        cloud_account_name: instance.details?.cloud_name,
        cloud_type: instance.details?.cloud_type,
        size: instance.meta?.flavor,
        tags: instance.tags,
      })),
    [instances]
  );

  const columns = useMemo(
    () => [
      powerScheduleInstance({
        idAccessor: "id",
        nameAccessor: "name",
        activeAccessor: "active",
        headerDataTestId: "lbl_instance",
        titleMessageId: "instance",
      }),
      resourcePoolOwner({
        id: "pool/owner",
        accessorFn: (rowOriginal) => {
          const { owner_name: ownerName } = rowOriginal;
          const { pool_name: poolName } = rowOriginal;

          return [poolName, ownerName].filter((str) => str !== "").join(" ");
        },
        getOwner: (rowOriginal) => {
          const { owner_name: ownerName } = rowOriginal;

          return {
            name: ownerName,
          };
        },
        getPool: (rowOriginal) => {
          const { pool_id: poolId, pool_name: poolName, pool_purpose: poolPurpose } = rowOriginal;

          return poolId
            ? {
                id: poolId,
                name: poolName,
                purpose: poolPurpose,
              }
            : undefined;
        },
      }),
      resourceLocation({
        idAccessor: "cloud_account_id",
        typeAccessor: "cloud_type",
        locationAccessors: {
          region: "region",
        },
        accessorKey: "cloud_account_name",
        headerDataTestId: "lbl_location",
      }),
      size({
        id: "size",
        accessorKey: "size",
        headerDataTestId: "lbl_size",
      }),
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (rowOriginal) => rowOriginal.tags ?? {},
      }),
    ],
    []
  );

  const actionBar = {
    show: true,
    definition: {
      items: [
        {
          key: "addInstancesToSchedule",
          icon: <AddOutlinedIcon fontSize="small" />,
          messageId: "addInstancesToSchedule",
          variant: "text",
          type: "button",
          dataTestId: "btn_add_instances_to_schedule",
          requiredActions: ["EDIT_PARTNER"],
          action: () => openSideModal(AddInstanceToScheduleModal, { powerScheduleId }),
        },
        (tableContext) => {
          const { rows: selectedRows } = tableContext.getFilteredSelectedRowModel();

          return {
            key: "removeInstancesFromSchedule",
            icon: <DeleteOutlinedIcon fontSize="small" />,
            messageId: "removeInstancesFromSchedule",
            type: "button",
            dataTestId: "btn_delete_instances_from_schedule",
            disabled: isEmptyArray(selectedRows),
            requiredActions: ["EDIT_PARTNER"],
            action: () =>
              openSideModal(RemoveInstancesFromScheduleModal, {
                powerScheduleId,
                selectedInstances: selectedRows.map(({ original }) => original),
              }),
          };
        },
      ],
    },
  };

  return (
    <Table
      withSelection
      withSearch
      queryParamPrefix="resource"
      pageSize={50}
      data={tableData}
      columns={columns}
      actionBar={actionBar}
      localization={{
        emptyMessageId: "noInstances",
      }}
    />
  );
};

export default PowerScheduleInstances;
