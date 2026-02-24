import { GET_AVAILABLE_FILTERS } from "api/restapi/actionTypes";
import RenameDataSourceForm from "components/forms/RenameDataSourceForm";
import { FormValues } from "components/forms/RenameDataSourceForm/types";
import { useUpdateDataSourceMutation } from "graphql/__generated__/hooks/restapi";
import { useRefetchApis } from "hooks/useRefetchApis";

const RenameDataSourceContainer = ({ id, name, closeSideModal }) => {
  const [updateDataSource, { loading }] = useUpdateDataSourceMutation();

  const refetch = useRefetchApis();

  const onSubmit = (formData: FormValues) => {
    updateDataSource({
      variables: {
        dataSourceId: id,
        params: {
          name: formData.name,
        },
      },
    }).then(() => {
      refetch([GET_AVAILABLE_FILTERS]);
      closeSideModal();
    });
  };

  return <RenameDataSourceForm name={name} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={loading} />;
};

export default RenameDataSourceContainer;
