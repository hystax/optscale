import SlicedText from "components/SlicedText";

type MlModelPathLabelProps = {
  path: string;
};

const PATH_LENGTH_LIMIT = 20;

const MlModelPathLabel = ({ path }: MlModelPathLabelProps) => <SlicedText limit={PATH_LENGTH_LIMIT} text={path} />;

export default MlModelPathLabel;
