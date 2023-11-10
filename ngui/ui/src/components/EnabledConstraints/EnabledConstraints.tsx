import { Fragment } from "react";
import { useConstraints } from "hooks/useConstraints";

const EnabledConstraints = ({ render }) => {
  const enabledConstraints = useConstraints();

  return enabledConstraints.map((type) => <Fragment key={type}>{render(type)}</Fragment>);
};

export default EnabledConstraints;
