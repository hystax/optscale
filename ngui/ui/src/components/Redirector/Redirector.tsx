import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

type RedirectorProps = {
  condition: boolean;
  to: string;
  replace?: boolean;
  children?: ReactNode;
};

const Redirector = ({ condition, to, replace = false, children = null }: RedirectorProps) =>
  condition ? <Navigate replace={replace} to={to} /> : children;

export default Redirector;
