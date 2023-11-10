import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import { getRecommendationsUrl } from "urls";

const RecommendationLink = ({ category, service, children, dataTestId }) => (
  <Link to={getRecommendationsUrl({ category, service })} component={RouterLink} data-test-id={dataTestId}>
    {children}
  </Link>
);

export default RecommendationLink;
