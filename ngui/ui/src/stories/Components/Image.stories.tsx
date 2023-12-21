import awsLogo from "assets/clouds/aws.svg";
import Image from "components/Image";

export default {
  component: Image
};

export const basic = () => <Image src={awsLogo} alt="altText" />;
