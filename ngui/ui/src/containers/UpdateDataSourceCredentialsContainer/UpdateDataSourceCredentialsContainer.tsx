import UpdateDataSourceCredentialsForm from "components/forms/UpdateDataSourceCredentialsForm";
import DataSourcesService from "services/DataSourcesService";

const UpdateDataSourceCredentialsContainer = ({ id, type, config, closeSideModal }) => {
  const { useUpdateDataSource } = DataSourcesService();

  const { isLoading, onUpdate } = useUpdateDataSource();

  const onSubmit = (...params) => {
    onUpdate(...params).then(() => closeSideModal());
  };

  return (
    <UpdateDataSourceCredentialsForm
      id={id}
      type={type}
      config={config}
      onSubmit={onSubmit}
      onCancel={closeSideModal}
      isLoading={isLoading}
    />
  );
};

export default UpdateDataSourceCredentialsContainer;
