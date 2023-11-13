import { S3_DUPLICATE_FINDER_CHECK } from "urls";
import BaseRoute from "./baseRoute";

class S3DuplicatesCheckRoute extends BaseRoute {
  page = "S3DuplicateFinderCheck";

  link = S3_DUPLICATE_FINDER_CHECK;
}

export default new S3DuplicatesCheckRoute();
