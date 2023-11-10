import { useFormContext } from "react-hook-form";

const ConnectForm = ({ children }) => {
  const methods = useFormContext();

  return children({ ...methods });
};

export default ConnectForm;
