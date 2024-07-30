import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { FormattedMessage } from "react-intl";
import { ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID } from "utils/constants";

type ArchivedRecommendationDescriptionProps = {
  reason: keyof typeof ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID;
  dataTestId?: string;
  isLoading?: boolean;
};

const ArchivedRecommendationDescription = ({
  reason,
  dataTestId,
  isLoading = false
}: ArchivedRecommendationDescriptionProps) => {
  if (isLoading) {
    return <Skeleton />;
  }

  return ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID[reason] ? (
    <Typography data-test-id={dataTestId}>
      <FormattedMessage id={ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID[reason]} />
    </Typography>
  ) : null;
};

export default ArchivedRecommendationDescription;
