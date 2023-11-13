import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS_VPC, AWS_EC2_VPC, AZURE_NETWORK, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FULL_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_obsolete_ips_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_obsolete_ips_location"
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_obsolete_ips_last_associated">
        <FormattedMessage id="lastSeenAssociated" />
      </TextWithDataTestId>
    ),
    accessorKey: "last_seen_active",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value, EN_FULL_FORMAT);
    }
  },
  detectedAt({ headerDataTestId: "lbl_obsolete_ips_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_obsolete_ips_cost">
        <FormattedMessage id="costInUnassociatedState" />
      </TextWithDataTestId>
    ),
    accessorKey: "cost_not_active_ip",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
    }
  },
  possibleMonthlySavings({
    headerDataTestId: "lbl_obsolete_ips_possible_monthly_savings",
    defaultSort: "desc"
  })
];

class ObsoleteIps extends BaseRecommendation {
  type = "obsolete_ips";

  name = "obsoleteIps";

  title = "obsoleteIpsTitle";

  descriptionMessageId = "obsoleteIpsDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  services = [AWS_EC2_VPC, AZURE_NETWORK, ALIBABA_ECS_VPC, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  emptyMessageId = "noObsoleteIps";

  withExclusions = true;

  static resourceDescriptionMessageId = "obsoleteIpsResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default ObsoleteIps;
