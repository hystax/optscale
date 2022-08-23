import { startTour, finishTour } from "./actionCreators";
import ProductTour from "./ProductTour";
import reducer, { TOURS, PRODUCT_TOUR, ENVIRONMENTS_TOUR } from "./reducer";

export default ProductTour;
export { reducer, TOURS, PRODUCT_TOUR, ENVIRONMENTS_TOUR };
export { startTour, finishTour };
