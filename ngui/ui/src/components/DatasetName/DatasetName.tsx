const DatasetName = ({ name, deleted = false }) => (deleted ? <s>{name}</s> : name);

export default DatasetName;
