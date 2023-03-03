import { intl } from "translations/react-intl-config";

class RecommendationFactory {
  configure() {
    return {
      type: this.type,
      moduleName: "",
      descriptionMessageId: "",
      emptyMessageId: "",
      dataTestIds: {}
    };
  }

  static configureColumns() {
    return [];
  }

  translate() {
    return intl.formatMessage({ id: this.messageId });
  }

  build(recommendations) {
    const recommendation = this.configure();

    recommendation.optimization = recommendations[recommendation.type] ?? {};

    recommendation.columns = this.constructor.configureColumns(recommendation.optimization);

    recommendation.translatedType = this.translate();

    return recommendation;
  }
}

export default RecommendationFactory;
