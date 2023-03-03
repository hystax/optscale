import { lazy } from "react";
import { v4 as uuidv4 } from "uuid";
import MainLayout from "layouts/MainLayout";

class BaseRoute {
  key = uuidv4();

  link = "";

  page = "";

  layout = MainLayout;

  component = lazy(() => import(`pages/${this.page}`));
}

export default BaseRoute;
