import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { size, mlExecutor, mlIOPSCap, mlLocalStorageBottleneckDuration, resourceLocation } from "utils/columns";
import BaseRecommendation from "../BaseRecommendation";

const columns = [
  mlExecutor({ showRunInspect: true }),
  resourceLocation({
    headerDataTestId: "lbl_location",
    idAccessor: "cloud_id",
    typeAccessor: "cloud_type",
    accessorKey: "cloud_name"
  }),
  size({
    accessorKey: "size"
  }),
  mlIOPSCap(),
  mlLocalStorageBottleneckDuration()
];

class LocalStorageBottleneck extends BaseRecommendation {
  type = "local_storage_bottleneck";

  name = "localStorageBottleneck";

  title = "localStorageBottleneck";

  descriptionMessageId = "localStorageBottleneckDescription";

  emptyMessageId = "noLocalStorageBottlenecks";

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
          key: "mlIOPSCap",
          value: <strong>{mlIOPSCap().cell({ row: { original: item } })}</strong>
        }
      ];
    });
  }

  columns = columns;
}

export default LocalStorageBottleneck;
