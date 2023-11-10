import { RESOURCE_LIFECYCLE_CREATE_POOL_POLICY } from "urls";
import BaseRoute from "./baseRoute";

class CreatePoolPolicyRoute extends BaseRoute {
  page = "CreatePoolPolicy";

  link = RESOURCE_LIFECYCLE_CREATE_POOL_POLICY;
}

export default new CreatePoolPolicyRoute();
