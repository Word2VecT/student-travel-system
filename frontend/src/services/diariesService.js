// src/services/diariesService.js
import { api } from './apiConfig';

export const fetchDiaries = async () => {
    try {
        const response = await api.get('/diaries');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch diaries:", error);
        throw error;
    }
};

export const fetchDiaryById = async (id) => {
    try {
        const response = await api.get(`/diaries/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch diary with ID ${id}:`, error);
        throw error;
    }
};

export const createDiary = async (diaryData) => {
    try {
        const response = await api.post('/diaries', diaryData);
        return response.data;
    } catch (error) {
        console.error("Failed to create diary:", error);
        throw error;
    }
};

export const deleteDiary = async (id) => {
    try {
        const response = await api.delete(`/diaries/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to delete diary with ID ${id}:`, error);
        throw error;
    }
};
