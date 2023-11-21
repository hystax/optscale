import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { size, mlExecutor, mlGpuMemoryUsage, resourceLocation } from "utils/columns";
import BaseRecommendation from "../BaseRecommendation";

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
  mlGpuMemoryUsage()
];

class GpuMemory extends BaseRecommendation {
  type = "gpu_memory";

  name = "gpuMemory";

  title = "gpuMemory";

  descriptionMessageId = "gpuMemoryDescription";

  emptyMessageId = "noRecommendations";

  categories = [];

  get previewItems() {
    return this.items.map((item) => {
      const { id, cloud_type: cloudType, cloud_resource_id: cloudResourceId, gpu_memory_usage: gpuMemoryUsage } = item;
      return [
        {
          key: "resource",
          node: (
            <IconLabel
              icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
              label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
            />
          )
        },
        {
          key: "mlGpuMemoryUsage",
          node: <strong>{mlGpuMemoryUsage().cell({ cell: { getValue: () => gpuMemoryUsage } })}</strong>
        }
      ];
    });
  }

  columns = columns;
}

export default GpuMemory;
