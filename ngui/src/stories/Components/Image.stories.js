import React from "react";
import awsLogo from "assets/clouds/aws.svg";
import Image from "components/Image";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Image`
};

export const basic = () => <Image src={awsLogo} alt="altText" />;
