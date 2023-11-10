import EnvironmentsCard from "components/EnvironmentsCard";
import EnvironmentsService from "services/EnvironmentsService";

const EnvironmentsCardContainer = () => {
  const { useGet } = EnvironmentsService();

  const { isGetEnvironmentsLoading, environments } = useGet();

  return <EnvironmentsCard isLoading={isGetEnvironmentsLoading} environments={environments} />;
};

export default EnvironmentsCardContainer;
