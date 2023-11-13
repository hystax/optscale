import { POOLS } from "urls";
import BaseRoute from "./baseRoute";

class PoolsRoute extends BaseRoute {
  page = "Pools";

  link = POOLS;
}

export default new PoolsRoute();
