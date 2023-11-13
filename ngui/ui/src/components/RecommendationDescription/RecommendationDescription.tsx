import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { FormattedMessage } from "react-intl";

const RecommendationDescription = ({ messageId, messageValues = {}, dataTestId, isLoading = false }) =>
  isLoading ? (
    <Skeleton />
  ) : (
    <Typography data-test-id={dataTestId}>
      <FormattedMessage id={messageId} values={messageValues} />
    </Typography>
  );

export default RecommendationDescription;
