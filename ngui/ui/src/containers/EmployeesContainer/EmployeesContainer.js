import React from "react";
import Employees from "components/Employees";
import EmployeesService from "services/EmployeesService";

const EmployeesContainer = () => {
  const { useGet } = EmployeesService();

  const { isLoading, employees } = useGet();

  return <Employees employees={employees} isLoading={isLoading} />;
};

export default EmployeesContainer;
