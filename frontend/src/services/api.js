import axios from 'axios';export const api=axios.create({baseURL:'/api'});export const message=e=>e.response?.data?.error||'Something went wrong. Please try again.';
