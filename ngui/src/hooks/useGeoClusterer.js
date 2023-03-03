import { sortObjects } from "utils/arrays";
import { getGeoDistance, getGeoPointBetween } from "utils/geo";

const MAXIMUM_ZOOM_DISTANCE = 1500;

const useGeoClusterer = (markers, zoom) => {
  const clusterDistance = MAXIMUM_ZOOM_DISTANCE / zoom;

  const clusters = [];

  // do not cluster already clustered markers
  const clusteredIndexes = new Set();

  markers.forEach((marker, i) => {
    if (clusteredIndexes.has(i)) {
      return;
    }

    const { latitude, longitude } = marker;
    const newCluster = [];
    for (let j = i + 1; j < markers.length; j += 1) {
      if (!clusteredIndexes.has(j)) {
        const anotherMarker = markers[j];
        const { latitude: latitude2, longitude: longitude2 } = anotherMarker;
        const distance = getGeoDistance(latitude, longitude, latitude2, longitude2);
        if (distance < clusterDistance) {
          clusteredIndexes.add(j);
          newCluster.push(anotherMarker);
        }
      }
    }

    if (newCluster.length) {
      clusteredIndexes.add(i);
      newCluster.push(marker);
      clusters.push(newCluster);
    }
  });

  const markersWithoutClusters = markers.filter((_, i) => !clusteredIndexes.has(i));
  const clusterMarkers = clusters.map((cluster, i) => {
    // averaging stuff
    const coordsList = [];
    let totalSum = 0;
    cluster.forEach(({ total, latitude, longitude }) => {
      totalSum += total;
      coordsList.push([latitude, longitude]);
    });
    const [latitude, longitude] = getGeoPointBetween(coordsList);

    // making definition, same as marker, but with isCluster and items (sorted markers array)
    const clusterDefinition = {
      id: "clusteredMarker",
      name: `cluster-${i}-${cluster.length}`,
      total: totalSum,
      latitude,
      longitude,
      isCluster: true,
      items: sortObjects({ array: cluster, field: "total" })
    };

    return clusterDefinition;
  });

  return markersWithoutClusters.concat(clusterMarkers);
};

export default useGeoClusterer;
