import { useEffect } from "react";
import { useParams } from "react-router-dom";
import ConnectJiraContainer from "containers/ConnectJiraContainer";
import { tag as tagHotjar } from "utils/hotjar";

const ConnectJira = () => {
  const { secret } = useParams();

  useEffect(() => {
    tagHotjar(["connected_jira"]);
  }, []);

  return <ConnectJiraContainer secret={secret} />;
};

export default ConnectJira;
