import React from "react";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import EmployeesTable from "components/EmployeesTable";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";

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
      <WrapperCard>
        <EmployeesTable employees={employees} isLoading={isLoading} />
      </WrapperCard>
    </PageContentWrapper>
  </>
);

Employees.propTypes = {
  employees: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default Employees;
