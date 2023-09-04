const NO_CONTENT = 204;

const makeRequest = async ({ url, options = {} }) =>
  window.AP.context
    .getToken()
    .then((token) => {
      const { headers = {}, method = "GET", ...restOptions } = options;

      const fetchOptions = {
        headers: {
          Authorization: `JWT ${token}`,
          ...headers
        },
        method,
        ...restOptions
      };

      return fetch(url, fetchOptions);
    })
    .then(async (response) => {
      if (response.ok) {
        const data = [NO_CONTENT].includes(response.status)
          ? {
              text: await response.text()
            }
          : await response.json();
        return Promise.resolve({
          data,
          error: null
        });
      }

      const { error } = await response.json();

      console.error(error.reason);

      return Promise.resolve({
        data: null,
        error
      });
    })
    .catch((error) => {
      console.error(error);
    });

export default makeRequest;
