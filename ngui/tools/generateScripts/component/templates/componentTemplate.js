module.exports = (componentName) => `import React from "react"
import PropTypes from "prop-types"
import useStyles from "./${componentName}.styles";

const ${componentName} = props => {
  const { classes } = useStyles();

  return (
    <div>

    </div>
  )
}

${componentName}.propTypes = {

}

export default ${componentName}
`;
