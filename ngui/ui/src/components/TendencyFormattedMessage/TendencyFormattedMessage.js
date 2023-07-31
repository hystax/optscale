import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { TENDENCY } from "utils/constants";

const getTendencyMessageId = (tendency) =>
  ({
    [TENDENCY.MORE]: "moreIsBetter",
    [TENDENCY.LESS]: "lessIsBetter"
  }[tendency]);

const TendencyFormattedMessage = ({ tendency }) => <FormattedMessage id={getTendencyMessageId(tendency)} />;

TendencyFormattedMessage.propTypes = {
  tendency: PropTypes.oneOf(Object.values(TENDENCY)).isRequired
};

export default TendencyFormattedMessage;
