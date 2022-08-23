import React from "react";
import { useLocation } from "react-router-dom";
import Mocked from "components/Mocked";
import { ResourcesMocked } from "components/Resources";
import ResourcesContainer from "containers/ResourcesContainer";

const Resources = () => {
  const { fromMainMenu = false } = useLocation();

  return (
    <Mocked mock={<ResourcesMocked />}>
      <ResourcesContainer fromMainMenu={fromMainMenu} />
    </Mocked>
  );
};

export default Resources;
