const DEGREE_IN_RADIANS = Math.PI / 180;

const RADIAN_IN_DEGREE = 180 / Math.PI;

const EARTH_RADIUS_IN_KM = 6371;

const EARTH_DIAMETER_IN_KM = 2 * EARTH_RADIUS_IN_KM;

const degreeToRadian = (degree) => degree * DEGREE_IN_RADIANS;

const radianToDegree = (radian) => radian * RADIAN_IN_DEGREE;

// https://stackoverflow.com/a/21623206
// eslint-disable-next-line
export const getGeoDistance = (lat1, lon1, lat2, lon2) => {
  const a =
    0.5 -
    Math.cos(degreeToRadian(lat2 - lat1)) / 2 +
    (Math.cos(degreeToRadian(lat1)) * Math.cos(degreeToRadian(lat2)) * (1 - Math.cos(degreeToRadian(lon2 - lon1)))) / 2;

  return EARTH_DIAMETER_IN_KM * Math.asin(Math.sqrt(a));
};

// https://stackoverflow.com/a/42234774
/**
 * Get a center latitude,longitude from an array of geopoints
 *
 * @param array data 2 dimensional array of latitudes and longitudes
 * For Example:
 * data = [
 *   [45.849382, 76.322333],
 *   [45.843543, 75.324143],
 *   [45.765744, 76.543223],
 *   [45.784234, 74.542335]
 * ];
 */
export const getGeoPointBetween = (data) => {
  const numCoords = data.length;

  let X = 0.0;
  let Y = 0.0;
  let Z = 0.0;

  for (let i = 0; i < numCoords; i += 1) {
    const lat = degreeToRadian(data[i][0]);
    const lon = degreeToRadian(data[i][1]);

    const a = Math.cos(lat) * Math.cos(lon);
    const b = Math.cos(lat) * Math.sin(lon);
    const c = Math.sin(lat);

    X += a;
    Y += b;
    Z += c;
  }

  X /= numCoords;
  Y /= numCoords;
  Z /= numCoords;

  const lon = Math.atan2(Y, X);
  const hyp = Math.sqrt(X * X + Y * Y);
  const lat = Math.atan2(Z, hyp);

  const newX = radianToDegree(lat);
  const newY = radianToDegree(lon);

  return [newX, newY];
};
