import React from "react";
import { FormattedMessage } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { firstSeen, lastUsed, size, mlExecutor, resourceLocation } from "utils/columns";
import BaseRecommendation from "../BaseRecommendation";

const columns = [
  mlExecutor(),
  lastUsed({
    defaultSort: "desc"
  }),
  firstSeen(),
  resourceLocation({
    headerDataTestId: "lbl_location",
    idAccessor: "cloud_id",
    typeAccessor: "cloud_type",
    accessorKey: "cloud_name"
  }),
  size({
    accessorKey: "size"
  })
];

class ExecutorsUpgrade extends BaseRecommendation {
  type = "executors_reservation";

  name = "executorsReservation";

  title = "reservationsForExecutors";

  descriptionMessageId = "reservationsForExecutorsDescription";

  emptyMessageId = "noExecutorsUpgrade";

  categories = [];

  get previewItems() {
    return this.items.map((item) => {
      const {
        id,
        cloud_type: cloudType,
        cloud_resource_id: cloudResourceId,
        recommended_size: recommendedSizeRaw,
        size: sizeRaw
      } = item;

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
          key: "size",
          value: (
            <strong>
              <FormattedMessage
                id="value -> value"
                values={{
                  value1: sizeRaw,
                  value2: recommendedSizeRaw
                }}
              />
            </strong>
          )
        }
      ];
    });
  }

  columns = columns;
}

export default ExecutorsUpgrade;
