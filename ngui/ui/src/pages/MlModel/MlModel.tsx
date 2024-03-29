import { useParams } from "react-router-dom";
import MlModelContainer from "containers/MlModelContainer";

const MlModel = () => {
  const { modelId } = useParams() as { modelId: string };

  return <MlModelContainer modelId={modelId} />;
};

export default MlModel;
