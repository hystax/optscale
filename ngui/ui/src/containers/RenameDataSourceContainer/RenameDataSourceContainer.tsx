import RenameDataSourceForm from "components/forms/RenameDataSourceForm";
import { FormValues } from "components/forms/RenameDataSourceForm/types";
import DataSourcesService from "services/DataSourcesService";

const RenameDataSourceContainer = ({ id, name, closeSideModal }) => {
  const { useUpdateDataSource } = DataSourcesService();

  const { isLoading, onUpdate } = useUpdateDataSource();

  const onSubmit = (formData: FormValues) => {
    onUpdate(id, { name: formData.name }).then(() => closeSideModal());
  };

  return <RenameDataSourceForm name={name} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={isLoading} />;
};

export default RenameDataSourceContainer;
