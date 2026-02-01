import axios from "axios";

// Tạo một kết nối chung
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // Lấy link từ file .env
  headers: {
    "Content-Type": "application/json",
  },
});

// Tự động chèn Token vào mỗi lần gửi yêu cầu
client.interceptors.request.use((config) => {
  // Lấy token từ localStorage (nơi lưu trữ chìa khóa khi đăng nhập)
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
