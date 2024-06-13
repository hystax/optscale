import UpdateDataSourceSkuForm from "components/forms/UpdateDataSourceSkuForm";
import DataSourceSkusService from "services/DataSourceSkusService";

const UpdateDataSourceSkuContainer = ({ sku, cost, costModel, dataSourceId, closeSideModal }) => {
  const { useUpdateDataSourceSku } = DataSourceSkusService();
  const { isLoading, onUpdate } = useUpdateDataSourceSku();

  const onSubmit = (formData) => {
    const value = { ...costModel, [sku]: formData.cost };
    onUpdate(dataSourceId, value).then(() => closeSideModal());
  };

  return <UpdateDataSourceSkuForm sku={sku} cost={cost} onSubmit={onSubmit} onCancel={closeSideModal} isLoading={isLoading} />;
};

export default UpdateDataSourceSkuContainer;
