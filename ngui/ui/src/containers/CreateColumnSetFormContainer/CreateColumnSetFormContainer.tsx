import CreateColumnSetForm from "components/CreateColumnSetForm";
import { getVisibleColumnIds } from "components/Table/utils";
import LayoutsService from "services/LayoutsService";
import { LAYOUT_TYPES } from "utils/constants";

const CreateColumnSetFormContainer = ({ tableContext }) => {
  const { useCreate } = LayoutsService();
  const { onCreate, isLoading: isCreateLayoutLoading } = useCreate();

  const createColumnSet = (name: string) => {
    const visibleColumnIds = getVisibleColumnIds(tableContext);

    return onCreate({
      name,
      data: JSON.stringify({
        columns: visibleColumnIds
      }),
      type: LAYOUT_TYPES.RESOURCE_RAW_EXPENSES_COLUMNS
    });
  };

  return (
    <CreateColumnSetForm
      onSubmit={createColumnSet}
      isLoadingProps={{
        isSubmitLoading: isCreateLayoutLoading
      }}
    />
  );
};

export default CreateColumnSetFormContainer;
