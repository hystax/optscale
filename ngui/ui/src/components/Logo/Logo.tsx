import Link from "@mui/material/Link";
import { useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import logo from "assets/logo/logo.svg";
import logoFullDemo from "assets/logo/logo_demo.svg";
import logoShortDemo from "assets/logo/logo_short_demo.svg";
import logoShortWhite from "assets/logo/logo_short_white.svg";
import logoShortWhiteDemo from "assets/logo/logo_short_white_demo.svg";
import logoFullWhite from "assets/logo/logo_white.svg";
import logoFullWhiteDemo from "assets/logo/logo_white_demo.svg";
import { HOME } from "urls";
import { LOGO_SIZE } from "utils/constants";
import { capitalize } from "utils/strings";

const logosMap = {
  logoFullWhite,
  logoShortWhite,
  logoFullDemo,
  logoShortDemo,
  logoFullWhiteDemo,
  logoShortWhiteDemo,
  logo
};

const getLogo = (demo, white, size) => {
  if (demo) {
    return logosMap[`logo${capitalize(size)}Demo`];
  }
  if (white) {
    return logosMap[`logo${capitalize(size)}White`];
  }
  return logosMap.logo;
};

const Logo = ({
  dataTestId,
  demo = false,
  active = false,
  white = false,
  width = "auto",
  height = "auto",
  size = LOGO_SIZE.FULL
}) => {
  const intl = useIntl();

  const renderLogo = (
    <img
      width={width}
      height={height}
      src={getLogo(demo, white, size)}
      alt={intl.formatMessage({ id: "optscale" })}
      data-test-id={dataTestId}
    />
  );

  return active ? (
    <Link component={RouterLink} to={HOME}>
      {renderLogo}
    </Link>
  ) : (
    renderLogo
  );
};

export default Logo;
