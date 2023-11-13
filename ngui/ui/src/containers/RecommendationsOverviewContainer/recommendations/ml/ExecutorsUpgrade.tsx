import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { lastUsed, mlExecutor, recommendedSize, resourceLocation, size } from "utils/columns";
import BaseRecommendation from "../BaseRecommendation";

const columns = [
  mlExecutor(),
  lastUsed({
    defaultSort: "desc"
  }),
  resourceLocation({
    headerDataTestId: "lbl_location",
    idAccessor: "cloud_id",
    typeAccessor: "cloud_type",
    accessorKey: "cloud_name"
  }),
  size({
    accessorKey: "size"
  }),
  recommendedSize({
    accessorKey: "recommended_size"
  })
];

class ExecutorsUpgrade extends BaseRecommendation {
  type = "executors_upgrade";

  name = "executorsUpgrade";

  title = "executorsUpgrade";

  descriptionMessageId = "executorsUpgradeDescription";

  emptyMessageId = "noExecutorsUpgrade";

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
        }
      ];
    });
  }

  columns = columns;
}

export default ExecutorsUpgrade;
