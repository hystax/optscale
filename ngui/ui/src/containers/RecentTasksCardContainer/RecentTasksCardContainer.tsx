import RecentTasksCard from "components/RecentTasksCard";
import MlTasksService from "services/MlTasksService";

const RecentTasksCardContainer = () => {
  const { useGetAll } = MlTasksService();
  const { tasks, isLoading } = useGetAll();

  return <RecentTasksCard tasks={tasks} isLoading={isLoading} />;
};

export default RecentTasksCardContainer;
