import jwt from "jsonwebtoken";

/**
 * Checks whether a given string represents a well-formed JSON Web Token (JWT).
 * This function uses the jwt.decode method to decode the token without verifying the signature.
 * If the decoding is successful and the decoded value is not null, the token is considered well-formed.
 * If an exception is thrown during decoding, or if the decoded value is null, the function returns false.
 *
 * @param {string} token - the JWT string to be checked.
 * @returns {boolean} true if the token is well-formed, false otherwise.
 */
const isValidJwt = (token) => {
  try {
    const jwtDecoded = jwt.decode(token);
    return jwtDecoded !== null;
  } catch (error) {
    return false;
  }
};

export default isValidJwt;
