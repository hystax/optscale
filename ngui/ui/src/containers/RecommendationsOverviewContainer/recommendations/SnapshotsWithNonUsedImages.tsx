import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import SnapshotsWithNonUsedImagesModal from "components/SideModalManager/SideModals/recommendations/SnapshotsWithNonUsedImagesModal";
import { ALIBABA_ECS, AWS_EC2 } from "hooks/useRecommendationServices";
import { isEmptyArray } from "utils/arrays";
import { detectedAt, firstSeenOn, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { ALIBABA_CNR, AWS_CNR, FORMATTED_MONEY_TYPES } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import { CELL_EMPTY_VALUE } from "utils/tables";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource(),
  resourceLocation(),
  firstSeenOn(),
  {
    header: <HeaderHelperCell titleMessageId="lastUsed" helperMessageId="snapshotsWithNonUsedImagesLastUsedHelp" />,
    accessorKey: "last_used",
    cell: ({ cell }: { cell: { getValue: () => number } }) => {
      const value = cell.getValue();
      return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
    },
  },
  {
    header: <FormattedMessage id="images" />,
    id: "images",
    cell: ({ row }: { row: { original: { images?: string[] } } }) => {
      const images = row.original.images ?? [];

      if (isEmptyArray(images)) {
        return CELL_EMPTY_VALUE;
      }

      return images.map((image) => (
        <Box key={image} sx={{ whiteSpace: "nowrap" }}>
          {image}
        </Box>
      ));
    },
  },
  detectedAt(),
  possibleMonthlySavings(),
];

class SnapshotsWithNonUsedImages extends BaseRecommendation {
  type = "snapshots_with_non_used_images";

  name = "snapshotsWithNonUsedImages";

  title = "snapshotsWithNonUsedImagesTitle";

  descriptionMessageId = "snapshotsWithNonUsedImagesDescription";

  services = [AWS_EC2, ALIBABA_ECS];

  appliedDataSources = [ALIBABA_CNR, AWS_CNR];

  categories = [CATEGORY.COST];

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  hasSettings = true;

  settingsSidemodalClass = SnapshotsWithNonUsedImagesModal;

  withCleanupScripts = false;

  emptyMessageId = "noSnapshotsWithNonUsedImages";

  dismissible = true;

  withExclusions = true;

  static resourceDescriptionMessageId = "snapshotWithNonUsedImagesRecommendation";

  get previewItems() {
    return this.items.map((item: { cloud_resource_id: string; resource_id: string; saving: number }) => [
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />,
      },
    ]);
  }

  columns = columns;
}

export default SnapshotsWithNonUsedImages;
