// src/services/apiConfig.js
import axios from 'axios';

export const api = axios.create({
    baseURL: 'http://localhost:5000/api', // 根据你的后端服务地址调整
});
