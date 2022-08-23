import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import airbus from "assets/customers/airbus.svg";
import bentley from "assets/customers/bentley.svg";
import dhl from "assets/customers/dhl.svg";
import nokia from "assets/customers/nokia.svg";
import pwc from "assets/customers/pwc.svg";
import tSystems from "assets/customers/t-systems.svg";
import yvesRocher from "assets/customers/yves-rocher.svg";
import SubTitle from "components/SubTitle";
import useStyles from "./CustomersGallery.styles";

const customersLogos = [
  {
    src: airbus,
    altMessageId: "airbus"
  },
  {
    src: pwc,
    altMessageId: "pwc"
  },
  {
    src: nokia,
    altMessageId: "nokia"
  },
  {
    src: bentley,
    altMessageId: "bentley"
  },
  {
    src: yvesRocher,
    altMessageId: "yvesRocher"
  },
  {
    src: dhl,
    altMessageId: "dhl"
  },
  {
    src: tSystems,
    altMessageId: "tSystems"
  }
];

const CustomersGallery = () => {
  const intl = useIntl();
  const { classes } = useStyles();

  return (
    <div data-test-id="div_meet_customer" className={classes.meetCustomersWrapper}>
      <SubTitle>
        <FormattedMessage id="trustedBy" />
      </SubTitle>
      <div className={classes.logosWrapper}>
        {customersLogos.map((item) => (
          <div className={classes.logoWrapper} key={item.altMessageId}>
            <img src={item.src} alt={intl.formatMessage({ id: item.altMessageId })} className={classes.logoImage} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CustomersGallery;
