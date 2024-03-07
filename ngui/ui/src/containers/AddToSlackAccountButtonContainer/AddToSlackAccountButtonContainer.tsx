import { useQuery } from "@apollo/client";
import ButtonLoader from "components/ButtonLoader";
import { GET_INSTALLATION_PATH } from "graphql/api/slacker/queries";
import SlackIcon from "icons/SlackIcon";

const AddToSlackAccountButtonContainer = () => {
  const { loading, data } = useQuery(GET_INSTALLATION_PATH);

  return (
    <ButtonLoader
      isLoading={loading}
      startIcon={<SlackIcon />}
      color="primary"
      variant="outlined"
      href={data?.url}
      messageId="addToSlack"
    />
  );
};

export default AddToSlackAccountButtonContainer;
