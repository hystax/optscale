import CloudAccountDetails from "components/CloudAccountDetails";
import { useDataSourceQuery } from "graphql/__generated__/hooks/restapi";

type CloudAccountDetailsContainerProps = {
  cloudAccountId: string;
};

const CloudAccountDetailsContainer = ({ cloudAccountId }: CloudAccountDetailsContainerProps) => {
  const { loading, data } = useDataSourceQuery({
    variables: {
      dataSourceId: cloudAccountId,
      requestParams: {
        details: true,
      },
    },
  });

  return <CloudAccountDetails data={data?.dataSource} isLoading={loading} />;
};

export default CloudAccountDetailsContainer;
