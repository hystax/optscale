import { useCallback } from "react";
import ColumnSets from "components/ColumnSets";
import { getHideableColumns } from "components/Table/utils";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import LayoutsService from "services/LayoutsService";
import { LAYOUT_TYPES } from "utils/constants";

const ColumnSetsContainer = ({ tableContext, closeSideModal }) => {
  const { organizationId } = useOrganizationInfo();

  const { useGetAll, useDelete, useGetOneOnDemand } = LayoutsService();
  const { onDelete, isLoading: isDeleteLayoutLoading, entityId: deletionEntityId } = useDelete();

  const { isLoading: isGetAllLayoutsLoading, layouts } = useGetAll({
    organizationId,
    layoutType: LAYOUT_TYPES.RESOURCE_RAW_EXPENSES_COLUMNS,
  });

  const { isLoading: isGetLayoutLoading, entityId: getLayoutEntityId, onGet } = useGetOneOnDemand();

  const deleteColumnSet = useCallback((id: string) => onDelete(id), [onDelete]);

  return (
    <ColumnSets
      columnSets={layouts}
      tableContext={tableContext}
      onApply={(columnsSetId) =>
        onGet(organizationId, columnsSetId).then(({ data }) => {
          const { columns: savedColumns } = JSON.parse(data);

          tableContext.setColumnVisibility(
            Object.fromEntries(
              getHideableColumns(tableContext).map(({ id: columnId }) => [columnId, savedColumns.includes(columnId)])
            )
          );
          closeSideModal();
        })
      }
      onDelete={(columnSetId) => deleteColumnSet(columnSetId)}
      isLoadingProps={{
        isGetAllColumnSetsLoading: isGetAllLayoutsLoading,
        getIsGetColumnSetLoading: (columnsSetId) => isGetLayoutLoading && getLayoutEntityId === columnsSetId,
        getIsDeleteColumnSetLoading: (columnsSetId) => isDeleteLayoutLoading && deletionEntityId === columnsSetId,
      }}
    />
  );
};

export default ColumnSetsContainer;
