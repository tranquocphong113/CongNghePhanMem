export const authStorageService = {
  // 1. Lưu Token
  setToken: (token: string) => {
    localStorage.setItem("access_token", token);
  },

  // 2. Lấy Token
  getToken: () => {
    return localStorage.getItem("access_token");
  },

  // 3. Xóa Token
  removeToken: () => {
    localStorage.removeItem("access_token");
  },

  // 4. Lưu thông tin User
  setCurrentUser: (user: any) => {
    localStorage.setItem("current_user", JSON.stringify(user));
  },

  // 5. Lấy thông tin User
  getCurrentUser: () => {
    const userStr = localStorage.getItem("current_user");
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  // 6. Xóa sạch (Đăng xuất)
  clear: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("current_user");
  },
};
