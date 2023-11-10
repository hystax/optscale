import { TTL_ANALYSIS } from "urls";
import BaseRoute from "./baseRoute";

class TtlAnalysisRoute extends BaseRoute {
  page = "TtlAnalysis";

  link = TTL_ANALYSIS;
}

export default new TtlAnalysisRoute();
