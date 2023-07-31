import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";

const ConnectForm = ({ children }) => {
  const methods = useFormContext();

  return children({ ...methods });
};

ConnectForm.propTypes = {
  children: PropTypes.func.isRequired
};

export default ConnectForm;
