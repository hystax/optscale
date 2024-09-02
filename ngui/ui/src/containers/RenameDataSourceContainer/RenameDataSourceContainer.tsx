import { useMutation } from "@apollo/client";
import RenameDataSourceForm from "components/forms/RenameDataSourceForm";
import { FormValues } from "components/forms/RenameDataSourceForm/types";
import { GET_DATA_SOURCE, UPDATE_DATA_SOURCE } from "graphql/api/restapi/queries/restapi.queries";

const RenameDataSourceContainer = ({ id, name, closeSideModal }) => {
  const [updateDataSource, { loading }] = useMutation(UPDATE_DATA_SOURCE);

  const onSubmit = (formData: FormValues) => {
    updateDataSource({
      variables: {
        dataSourceId: id,
        params: {
          name: formData.name
        }
      },
      refetchQueries: [GET_DATA_SOURCE]
    }).then(() => closeSideModal());
  };

  return <RenameDataSourceForm name={name} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={loading} />;
};

export default RenameDataSourceContainer;
