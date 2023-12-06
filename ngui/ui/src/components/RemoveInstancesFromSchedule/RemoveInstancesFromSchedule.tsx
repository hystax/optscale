import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import DeleteEntity from "components/DeleteEntity";
import ResourceLabel from "components/ResourceLabel";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { resourceLocation } from "utils/columns";
import { getCloudResourceIdentifier } from "utils/resources";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const RemoveInstancesFromSchedule = ({ instancesToRemove, onDelete, onCancel, isLoading = false }) => {
  const tableData = useMemo(() => instancesToRemove, [instancesToRemove]);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_instance">
            <FormattedMessage id="instance" />
          </TextWithDataTestId>
        ),
        id: "instance",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        cell: ({ row: { original } }) => (
          <CaptionedCell caption={original.name}>
            <ResourceLabel resourceId={original.id} cloudResourceIdentifier={getCloudResourceIdentifier(original)} />
          </CaptionedCell>
        )
      },
      resourceLocation({
        idAccessor: "cloud_account_id",
        typeAccessor: "cloud_type",
        locationAccessors: {
          region: "region"
        },
        accessorKey: "cloud_account_name",
        headerDataTestId: "lbl_location"
      })
    ],
    []
  );

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        messageId: "remove",
        onDelete
      }}
      dataTestIds={{
        text: "p_remove_instances_from_schedule",
        deleteButton: "btn_remove_instances_from_schedule_delete",
        cancelButton: "btn_remove_instances_from_schedule_cancel"
      }}
      message={{
        messageId: "removeInstancedFromScheduleQuestion"
      }}
    >
      <Table
        data={tableData}
        columns={columns}
        localization={{
          emptyMessageId: "noInstances"
        }}
      />
    </DeleteEntity>
  );
};

export default RemoveInstancesFromSchedule;
