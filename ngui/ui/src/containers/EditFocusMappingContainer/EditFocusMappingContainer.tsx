import type { ApiMapping } from "components/FocusMappingEditor";
import EditFocusMappingForm from "components/forms/EditFocusMappingForm";
import { useUpdateDataSourceMutation } from "graphql/__generated__/hooks/restapi";

type EditFocusMappingContainerProps = {
  id: string;
  mapping?: ApiMapping | null;
  closeSideModal: () => void;
};

const EditFocusMappingContainer = ({ id, mapping, closeSideModal }: EditFocusMappingContainerProps) => {
  const [updateDataSource, { loading }] = useUpdateDataSourceMutation();

  // Only the mapping is sent, so the connection config and the keys stay unchanged; null resets the mapping to defaults
  const onSubmit = (updatedMapping: ApiMapping | null) => {
    updateDataSource({
      variables: {
        dataSourceId: id,
        params: {
          mapping: updatedMapping,
        },
      },
    }).then(() => {
      closeSideModal();
    });
  };

  return <EditFocusMappingForm mapping={mapping} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={loading} />;
};

export default EditFocusMappingContainer;
