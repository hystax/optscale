import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import FormattedDigitalUnit from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import {
  mlExecutor,
  mlComputeLocation,
  mlDataLocation,
  mlDataTransferred,
  estimatedExpenses as estimatedExpensesColumn
} from "utils/columns";
import BaseRecommendation from "../BaseRecommendation";

const columns = [mlExecutor(), mlComputeLocation(), mlDataLocation(), mlDataTransferred(), estimatedExpensesColumn()];

class CrossRegionTraffic extends BaseRecommendation {
  type = "cross_region_traffic";

  name = "crossRegionTraffic";

  title = "crossRegionTraffic";

  descriptionMessageId = "crossRegionTrafficDescription";

  emptyMessageId = "noCrossRegionTraffic";

  categories = [];

  get previewItems() {
    return this.items.map((item) => {
      const {
        id,
        cloud_type: cloudType,
        cloud_resource_id: cloudResourceId,
        data_transferred: dataTransferred,
        estimated_expenses: estimatedExpenses
      } = item;
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
          key: "dataTransferred",
          node: (
            <strong>
              <FormattedDigitalUnit value={dataTransferred} />
            </strong>
          )
        },
        {
          key: "expenses",
          node: (
            <strong>
              <FormattedMoney value={estimatedExpenses} />
            </strong>
          )
        }
      ];
    });
  }

  columns = columns;
}

export default CrossRegionTraffic;
