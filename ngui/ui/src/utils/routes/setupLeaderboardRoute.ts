import { ML_SETUP_LEADERBOARDS } from "urls";
import BaseRoute from "./baseRoute";

class PoolsRoute extends BaseRoute {
  page = "SetupLeaderboard";

  link = ML_SETUP_LEADERBOARDS;
}

export default new PoolsRoute();
