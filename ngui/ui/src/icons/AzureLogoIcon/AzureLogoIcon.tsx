import SvgIcon from "@mui/material/SvgIcon";

const AzureLogoIcon = (props) => (
  <SvgIcon {...props}>
    <defs>
      <style>
        {`.a{fill:url(#a);}
            .b{fill:#0078d4;}
            .c{fill:url(#b);}
            .d{fill:url(#c);}`}
      </style>
      <linearGradient
        id="a"
        x1="-1267.51517"
        y1="546.48352"
        x2="-1271.44232"
        y2="558.08531"
        gradientTransform="translate(1991.3125 -849.89368) scale(1.5625)"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0" stopColor="#114a8b" />
        <stop offset="1" stopColor="#0669bc" />
      </linearGradient>
      <linearGradient
        id="b"
        x1="-1266.28536"
        y1="551.89124"
        x2="-1267.19466"
        y2="552.1987"
        gradientTransform="translate(1991.3125 -849.89368) scale(1.5625)"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0" stopOpacity="0.3" />
        <stop offset="0.071" stopOpacity="0.2" />
        <stop offset="0.321" stopOpacity="0.1" />
        <stop offset="0.623" stopOpacity="0.05" />
        <stop offset="1" stopOpacity="0" />
      </linearGradient>
      <linearGradient
        id="c"
        x1="-1266.75241"
        y1="546.13435"
        x2="-1262.44136"
        y2="557.61979"
        gradientTransform="translate(1991.3125 -849.89368) scale(1.5625)"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0" stopColor="#3ccbf4" />
        <stop offset="1" stopColor="#2892df" />
      </linearGradient>
    </defs>
    <path
      className="a"
      d="M8.66744,2.59618h5.91818L8.442,20.76322a.94357.94357,0,0,1-.89394.6406H2.94223a.94.94,0,0,1-.8928-1.24082L7.77328,3.23678A.94356.94356,0,0,1,8.66744,2.596Z"
    />
    <path
      className="b"
      d="M17.26742,14.78141H7.88261A.43333.43333,0,0,0,7.586,15.532l6.03046,5.6175a.94906.94906,0,0,0,.64687.25429h5.314Z"
    />
    <path
      className="c"
      d="M8.66744,2.59618a.9358.9358,0,0,0-.89621.65308L2.05648,20.14757a.94.94,0,0,0,.88825,1.25625H7.66941a1.00928,1.00928,0,0,0,.77506-.65784L9.5841,17.394l4.07077,3.78938a.96419.96419,0,0,0,.606.22049h5.29427l-2.322-6.62241-6.76893.00159L14.607,2.59618Z"
    />
    <path
      className="d"
      d="M16.22643,3.23587a.942.942,0,0,0-.8928-.63969H8.7379a.94218.94218,0,0,1,.89279.63969l5.72408,16.9269a.94144.94144,0,0,1-.8928,1.24128h6.596a.94023.94023,0,0,0,.89256-1.24128Z"
    />
  </SvgIcon>
);

export default AzureLogoIcon;
