import { S3_DUPLICATE_FINDER } from "urls";
import BaseRoute from "./baseRoute";

class S3DuplicateFinderRoute extends BaseRoute {
  page = "S3DuplicateFinder";

  link = S3_DUPLICATE_FINDER;
}

export default new S3DuplicateFinderRoute();
