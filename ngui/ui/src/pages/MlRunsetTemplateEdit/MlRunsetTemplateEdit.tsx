import Protector from "components/Protector";
import MlRunsetTemplateEditContainer from "containers/MlRunsetTemplateEditContainer";

const MlRunsetTemplateEdit = () => (
  <Protector allowedAction={["EDIT_PARTNER"]}>
    <MlRunsetTemplateEditContainer />
  </Protector>
);

export default MlRunsetTemplateEdit;
