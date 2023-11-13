import { CloudAccountsOverviewMocked } from "components/CloudAccountsOverview";
import Mocked from "components/Mocked";
import GetCloudAccountsContainer from "containers/GetCloudAccountsContainer";

const CloudAccountsOverview = () => (
  <Mocked mock={<CloudAccountsOverviewMocked />}>
    <GetCloudAccountsContainer />
  </Mocked>
);

export default CloudAccountsOverview;
