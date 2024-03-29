import SlicedText from "components/SlicedText";

type MlModelVersionLabelProps = {
  version: string;
};

const VERSION_LENGTH_LIMIT = 20;

const MlModelVersionLabel = ({ version }: MlModelVersionLabelProps) => (
  <SlicedText limit={VERSION_LENGTH_LIMIT} text={version} />
);

export default MlModelVersionLabel;
