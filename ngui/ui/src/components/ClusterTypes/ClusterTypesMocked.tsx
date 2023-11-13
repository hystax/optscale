import ClusterTypes from "./ClusterTypes";

const ClusterTypesMocked = () => (
  <ClusterTypes
    clusterTypes={[
      {
        name: "Purpose",
        tag_key: "purpose",
        priority: 1
      },
      {
        name: "Created by",
        tag_key: "aws:createdby",
        priority: 2
      },
      {
        name: "Marketing",
        tag_key: "marketing",
        priority: 3
      }
    ]}
  />
);

export default ClusterTypesMocked;
