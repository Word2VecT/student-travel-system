// src/services/routeService.js
import { api } from './apiConfig';

export const fetchRoute = async (startLocationId, endLocationId) => {
    try {
        const response = await api.get(`/route?start=${startLocationId}&end=${endLocationId}`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch route:", error);
        throw error;
    }
};
