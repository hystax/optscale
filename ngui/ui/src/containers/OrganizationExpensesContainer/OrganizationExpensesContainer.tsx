import OrganizationExpenses from "components/OrganizationExpenses";
import ExpensesService from "services/ExpensesService";

const OrganizationExpensesContainer = () => {
  const { useGetOrganizationExpenses } = ExpensesService();

  const { isLoading, data } = useGetOrganizationExpenses();

  return <OrganizationExpenses data={data} isLoading={isLoading} />;
};

export default OrganizationExpensesContainer;
