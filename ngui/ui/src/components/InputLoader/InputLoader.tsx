import Input from "components/Input";
import Skeleton from "components/Skeleton";

const InputLoader = ({ margin = "dense", fullWidth }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Input margin={margin} />
  </Skeleton>
);

export default InputLoader;
