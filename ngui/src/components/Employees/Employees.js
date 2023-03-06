import React from "react";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import EmployeesTable from "components/EmployeesTable";
import PageContentWrapper from "components/PageContentWrapper";

const Employees = ({ employees, isLoading }) => (
  <>
    <ActionBar
      data={{
        title: {
          messageId: "users",
          dataTestId: "lbl_users"
        }
      }}
    />
    <PageContentWrapper>
      <EmployeesTable employees={employees} isLoading={isLoading} />
    </PageContentWrapper>
  </>
);

Employees.propTypes = {
  employees: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default Employees;
