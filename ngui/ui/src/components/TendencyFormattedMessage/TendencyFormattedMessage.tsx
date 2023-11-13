import { FormattedMessage } from "react-intl";
import { TENDENCY } from "utils/constants";

const getTendencyMessageId = (tendency) =>
  ({
    [TENDENCY.MORE]: "moreIsBetter",
    [TENDENCY.LESS]: "lessIsBetter"
  })[tendency];

const TendencyFormattedMessage = ({ tendency }) => <FormattedMessage id={getTendencyMessageId(tendency)} />;

export default TendencyFormattedMessage;
