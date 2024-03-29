import { useParams } from "react-router-dom";
import Protector from "components/Protector";
import MlEditModelContainer from "containers/MlEditModelContainer";

const MlEditModel = () => {
  const { modelId } = useParams() as { modelId: string };

  return (
    <Protector allowedActions={["EDIT_PARTNER"]}>
      <MlEditModelContainer modelId={modelId} />
    </Protector>
  );
};

export default MlEditModel;
