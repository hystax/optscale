import { useQuery } from "@apollo/client";
import CloudAccountDetails from "components/CloudAccountDetails";
import { GET_DATA_SOURCE } from "graphql/api/restapi/queries";

type CloudAccountDetailsContainerProps = {
  cloudAccountId: string;
};

const CloudAccountDetailsContainer = ({ cloudAccountId }: CloudAccountDetailsContainerProps) => {
  const { loading, data } = useQuery(GET_DATA_SOURCE, {
    variables: {
      dataSourceId: cloudAccountId,
      requestParams: {
        details: true
      }
    }
  });

  return <CloudAccountDetails data={data?.dataSource} isLoading={loading} />;
};

export default CloudAccountDetailsContainer;
