import { LocalFlowmapDataProvider } from "@flowmap.gl/data";
import FlowMapSelectors from "./FlowMapSelectors";

export default class FlowMapDataProvider extends LocalFlowmapDataProvider {
  constructor(accessors) {
    super(accessors);
    this.selectors = new FlowMapSelectors(accessors);
  }
}
