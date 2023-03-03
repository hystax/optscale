import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_OBSOLETE_IPS, OBSOLETE_IPS_TYPE, FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FULL_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "utils/recommendations";

class ObsoleteIpsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_OBSOLETE_IPS;

  moduleName = OBSOLETE_IPS_TYPE;

  withExclusions = true;

  messageId = "obsoleteIpsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "obsoleteIpsDescription",
      emptyMessageId: "noObsoleteIps",
      dataTestIds: {
        listTestId: "sp_obsolete_ips",
        textTestId: "p_obsolete_ips",
        buttonTestIds: ["btn_obsolete_ips_download"]
      }
    };
  }

  static configureColumns() {
    return [
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
  }
}

export default new ObsoleteIpsRecommendation();
