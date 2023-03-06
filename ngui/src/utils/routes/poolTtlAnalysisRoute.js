import { POOL_TTL_ANALYSIS } from "urls";
import BaseRoute from "./baseRoute";

class PoolTtlAnalysisRoute extends BaseRoute {
  page = "TtlAnalysis";

  link = POOL_TTL_ANALYSIS;
}

export default new PoolTtlAnalysisRoute();
