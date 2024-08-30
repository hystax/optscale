import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import { CLOUD_ACCOUNT_CONNECT } from "urls";
import { OPTSCALE_MODE } from "utils/constants";
import dataSources from "utils/routes/dataSourcesRoute";
import BaseMenuItem from "./baseMenuItem";

class DataSourcesMenuItem extends BaseMenuItem {
  route = dataSources;

  // eslint-disable-next-line class-methods-use-this
  messageId = ({ mode }) => {
    if (mode?.[OPTSCALE_MODE.FINOPS] ?? true) {
      return "dataSources";
    }

    return "cloudConnections";
  };

  dataTestId = "btn_cloud_accs";

  dataProductTourId = PRODUCT_TOUR_IDS.DATA_SOURCES;

  icon = CloudOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath === CLOUD_ACCOUNT_CONNECT;
}

export default new DataSourcesMenuItem();
