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

export default Employees;
