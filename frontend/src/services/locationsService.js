// src/services/locationsService.js
import { api } from './apiConfig';

export const fetchLocations = async () => {
    try {
        const response = await api.get('/locations');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch locations:", error);
        throw error;
    }
};

export const fetchLocationById = async (id) => {
    try {
        const response = await api.get(`/locations/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch location with ID ${id}:`, error);
        throw error;
    }
};
