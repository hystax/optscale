import { startTour, finishTour } from "./actionCreators";
import { ENVIRONMENTS_TOUR_IDS, PRODUCT_TOUR_IDS } from "./definitions";
import { useStartTour, useProductTour } from "./hooks";
import reducer, { TOURS, PRODUCT_TOUR, ENVIRONMENTS_TOUR } from "./reducer";
import Tour from "./Tour";

export { useStartTour };

export { reducer, TOURS, PRODUCT_TOUR, ENVIRONMENTS_TOUR, useProductTour };
export { startTour, finishTour };
export { ENVIRONMENTS_TOUR_IDS, PRODUCT_TOUR_IDS };

export default Tour;
