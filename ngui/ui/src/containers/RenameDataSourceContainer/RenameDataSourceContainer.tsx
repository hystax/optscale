import RenameDataSourceForm from "components/RenameDataSourceForm";
import DataSourcesService from "services/DataSourcesService";

const RenameDataSourceContainer = ({ id, name, closeSideModal }) => {
  const { useUpdateDataSource } = DataSourcesService();

  const { isLoading, onUpdate } = useUpdateDataSource();

  const onSubmit = (newName) => {
    onUpdate(id, { name: newName }).then(() => closeSideModal());
  };

  return <RenameDataSourceForm name={name} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={isLoading} />;
};

export default RenameDataSourceContainer;
