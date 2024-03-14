const checkEnvironment = (requiredVariables: string[]) => {
  requiredVariables.forEach((variable) => {
    if (!process.env[variable]) {
      console.warn(
        `\x1b[31mRequired environment variable ${variable} is not set\x1b[0m`
      );
    }
  });
};

export default checkEnvironment;
