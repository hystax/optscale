export const getParams = <T>(requestParams: T) =>
  new URLSearchParams(
    Object.entries(requestParams)
      .filter(
        ([, value]) =>
          // TODO: investigate if we can handle only either undefined or null values
          value !== undefined && value !== null
      )
      .flatMap(([key, value]) => {
        if (Array.isArray(value)) {
          return value.map((v) => [key, v.toString()]);
        }
        return [[key, value.toString()]];
      }) as [string, string][]
  );
