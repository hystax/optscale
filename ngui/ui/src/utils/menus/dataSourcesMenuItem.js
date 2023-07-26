import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import { CLOUD_ACCOUNT_CONNECT } from "urls";
import dataSources from "utils/routes/dataSourcesRoute";
import BaseMenuItem from "./baseMenuItem";

class DataSourcesMenuItem extends BaseMenuItem {
  route = dataSources;

  messageId = "dataSourcesTitle";

  dataTestId = "btn_cloud_accs";

  dataProductTourId = PRODUCT_TOUR_IDS.DATA_SOURCES;

  icon = CloudOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath === CLOUD_ACCOUNT_CONNECT;
}

export default new DataSourcesMenuItem();
