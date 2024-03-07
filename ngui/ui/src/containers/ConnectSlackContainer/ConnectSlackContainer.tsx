import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import ConnectSlack from "components/ConnectSlack";
import { CONNECT_SLACK_USER } from "graphql/api/slacker/queries";

type ConnectSlackContainerProps = {
  secret: string;
};

const ConnectSlackContainer = ({ secret }: ConnectSlackContainerProps) => {
  const [connectSlackUser, { loading, error }] = useMutation(CONNECT_SLACK_USER, {
    variables: {
      secret
    }
  });

  useEffect(() => {
    connectSlackUser();
  }, [connectSlackUser, secret]);

  return <ConnectSlack isLoading={loading} isError={!!error} />;
};

export default ConnectSlackContainer;
