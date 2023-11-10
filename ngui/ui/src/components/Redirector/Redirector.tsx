import { Navigate } from "react-router-dom";

const Redirector = ({ children = null, condition, to, replace = false }) =>
  condition ? <Navigate replace={replace} to={to} /> : children;

export default Redirector;
