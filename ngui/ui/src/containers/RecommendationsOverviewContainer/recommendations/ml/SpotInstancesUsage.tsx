import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { useFormatDuration } from "hooks/useFormatDuration";
import { mlRunsCount, size, mlAverageLifetime, mlExecutor, resourceLocation } from "utils/columns";
import { secondsToMilliseconds } from "utils/datetime";
import BaseRecommendation from "../BaseRecommendation";

const FormattedApproximateAverageLifetime = ({ lifetime }) => {
  const time = useFormatDuration(secondsToMilliseconds(lifetime), 1);

  return `~${time}`;
};

const columns = [
  mlExecutor(),
  resourceLocation({
    headerDataTestId: "lbl_location",
    idAccessor: "cloud_id",
    typeAccessor: "cloud_type",
    accessorKey: "cloud_name"
  }),
  size({
    accessorKey: "size",
    headerDataTestId: "lbl_size"
  }),
  mlRunsCount(),
  mlAverageLifetime()
];

class SpotInstancesUsage extends BaseRecommendation {
  type = "spot_instances_usage";

  name = "spotInstancesUsage";

  title = "spotPreemptibleInstancesUsage";

  descriptionMessageId = "spotPreemptibleInstancesUsageDescription";

  emptyMessageId = "noSpotPreemptibleOnstancesUsage";

  categories = [];

  get previewItems() {
    return this.items.map((item) => {
      const { id, cloud_type: cloudType, cloud_resource_id: cloudResourceId } = item;

      return [
        {
          key: "resource",
          value: (
            <IconLabel
              icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
              label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
            />
          )
        },
        {
          key: "averageLifetime",
          value: (
            <strong>
              <FormattedApproximateAverageLifetime lifetime={item.average_lifetime} />
            </strong>
          )
        }
      ];
    });
  }

  columns = columns;
}

export default SpotInstancesUsage;
