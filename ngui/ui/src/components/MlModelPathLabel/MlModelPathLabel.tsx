import CopyText from "components/CopyText";
import SlicedText from "components/SlicedText";

type MlModelPathLabelProps = {
  path: string;
};

const PATH_LENGTH_LIMIT = 70;

const MlModelPathLabel = ({ path }: MlModelPathLabelProps) => (
  <CopyText text={path}>
    <SlicedText limit={PATH_LENGTH_LIMIT} text={path} />
  </CopyText>
);

export default MlModelPathLabel;
