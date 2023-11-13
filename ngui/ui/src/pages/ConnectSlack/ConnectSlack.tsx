import { useEffect } from "react";
import { useParams } from "react-router-dom";
import ConnectSlackContainer from "containers/ConnectSlackContainer";
import { tag as tagHotjar } from "utils/hotjar";

const ConnectSlack = () => {
  const { secret } = useParams();

  useEffect(() => {
    tagHotjar(["connected_slack"]);
  }, []);

  return <ConnectSlackContainer secret={secret} />;
};

export default ConnectSlack;
