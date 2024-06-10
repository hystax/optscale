import RecentModelsCard from "components/RecentModelsCard";
import MlModelsService from "services/MlModelsService";

const RecentModelsCardContainer = () => {
  const { useGetAll } = MlModelsService();
  const { isLoading, models } = useGetAll();

  return <RecentModelsCard models={models} isLoading={isLoading} />;
};

export default RecentModelsCardContainer;
