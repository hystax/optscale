import { useEffect } from "react";
import ConnectSlack from "components/ConnectSlack";
import { useConnectSlackUserMutation } from "graphql/__generated__/hooks/slacker";

type ConnectSlackContainerProps = {
  secret: string;
};

const ConnectSlackContainer = ({ secret }: ConnectSlackContainerProps) => {
  const [connectSlackUser, { loading, error }] = useConnectSlackUserMutation({
    variables: {
      secret,
    },
  });

  useEffect(() => {
    connectSlackUser();
  }, [connectSlackUser, secret]);

  return <ConnectSlack isLoading={loading} isError={!!error} />;
};

export default ConnectSlackContainer;
