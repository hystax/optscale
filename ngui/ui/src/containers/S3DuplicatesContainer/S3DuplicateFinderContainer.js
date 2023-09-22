import React from "react";
import S3DuplicateFinder from "components/S3DuplicateFinder";
import S3DuplicatesService from "services/S3DuplicatesService";

const S3DuplicateFinderContainer = () => {
  const { useGetAll } = S3DuplicatesService();

  const { isLoading, geminis } = useGetAll();

  return <S3DuplicateFinder geminis={geminis} isLoading={isLoading} />;
};

export default S3DuplicateFinderContainer;
