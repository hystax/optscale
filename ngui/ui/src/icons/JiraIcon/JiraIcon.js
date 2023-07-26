import React from "react";
import createSvgIcon from "@mui/icons-material/utils/createSvgIcon";

const JiraIcon = createSvgIcon(
  <>
    <defs>
      <linearGradient
        id="a"
        x1="-212.11407"
        y1="19.6918"
        x2="-212.48853"
        y2="20.06618"
        gradientTransform="translate(2350.66837 -211.11028) scale(11.02802)"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.18" stopColor="#0052cc" />
        <stop offset="1" stopColor="#2684ff" />
      </linearGradient>
      <linearGradient id="b" x1="-212.01492" y1="20.76745" x2="-211.64119" y2="20.39381" xlinkHref="#a" />
    </defs>
    <path
      fill="#2684ff"
      d="M21.43914,11.44018,12.83289,2.83393,11.999,2,5.52039,8.47857l-2.9625,2.96161a.79374.79374,0,0,0,0,1.11964l5.91875,5.91875L11.999,22l6.47768-6.47857.10089-.1,2.86161-2.85714a.792.792,0,0,0,.00411-1.12l-.00411-.00411Zm-9.44018,3.517L9.04181,12,11.999,9.04286,14.95521,12Z"
    />
    <path fill="url('#a')" d="M11.999,9.04286a4.97768,4.97768,0,0,1-.02143-7.01875L5.507,8.492l3.52143,3.52143Z" />
    <path fill="url('#b')" d="M14.96324,11.992,11.999,14.95714a4.97947,4.97947,0,0,1,0,7.04107l6.48839-6.48482Z" />
  </>
);

export default JiraIcon;
