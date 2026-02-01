import { Tenant } from "@/types";

// Key lưu trong LocalStorage
const WORKSPACES_KEY = "fusion_workspaces";
const MEMBERSHIPS_KEY = "fusion_memberships";

export interface Workspace extends Tenant {
  ownerId: string;
  inviteCode: string; // Mã mời
}

interface Membership {
  userId: string;
  workspaceId: string;
  role: "admin" | "member";
}

export const workspaceStorageService = {
  // 1. Lấy danh sách Workspace của User đang đăng nhập
  getUserWorkspaces: (userId: string): Workspace[] => {
    const allWorkspaces = workspaceStorageService.getAllWorkspaces();
    const allMemberships = workspaceStorageService.getAllMemberships();

    // Lọc ra những workspace mà user này là thành viên
    const userMemberships = allMemberships.filter((m) => m.userId === userId);
    const workspaceIds = userMemberships.map((m) => m.workspaceId);

    return allWorkspaces.filter((w) => workspaceIds.includes(w.id));
  },

  // 2. Tạo Workspace mới (Kèm mã mời)
  createWorkspace: (userId: string, name: string): Workspace => {
    const allWorkspaces = workspaceStorageService.getAllWorkspaces();

    const newWorkspace: Workspace = {
      id: "ws_" + Date.now(), // ID tự sinh
      name: name,
      slug: name.toLowerCase().replace(/\s+/g, "-"),
      themeAccent: "blue-600", // Mặc định
      ownerId: userId,
      inviteCode: Math.random().toString(36).substring(2, 8).toUpperCase(), // Mã ngẫu nhiên 6 ký tự
    };

    // Lưu Workspace
    allWorkspaces.push(newWorkspace);
    localStorage.setItem(WORKSPACES_KEY, JSON.stringify(allWorkspaces));

    // Tạo luôn Membership cho người tạo (là Admin)
    workspaceStorageService.addMember(userId, newWorkspace.id, "admin");

    return newWorkspace;
  },

  // 3. Tham gia Workspace bằng Mã mời
  joinByInviteCode: (userId: string, code: string): boolean => {
    const allWorkspaces = workspaceStorageService.getAllWorkspaces();
    const targetWorkspace = allWorkspaces.find((w) => w.inviteCode === code);

    if (!targetWorkspace) return false; // Không tìm thấy mã

    // Kiểm tra xem đã tham gia chưa
    const allMemberships = workspaceStorageService.getAllMemberships();
    const exists = allMemberships.some(
      (m) => m.userId === userId && m.workspaceId === targetWorkspace.id,
    );

    if (!exists) {
      workspaceStorageService.addMember(userId, targetWorkspace.id, "member");
    }
    return true;
  },

  // --- Các hàm phụ trợ (Private) ---
  getAllWorkspaces: (): Workspace[] => {
    return JSON.parse(localStorage.getItem(WORKSPACES_KEY) || "[]");
  },

  getAllMemberships: (): Membership[] => {
    return JSON.parse(localStorage.getItem(MEMBERSHIPS_KEY) || "[]");
  },

  addMember: (
    userId: string,
    workspaceId: string,
    role: "admin" | "member",
  ) => {
    const members = workspaceStorageService.getAllMemberships();
    members.push({ userId, workspaceId, role });
    localStorage.setItem(MEMBERSHIPS_KEY, JSON.stringify(members));
  },

  // Hàm khởi tạo dữ liệu mẫu nếu chưa có gì (Cho lần chạy đầu tiên)
  initSampleData: (userId: string) => {
    const ws = workspaceStorageService.getUserWorkspaces(userId);
    if (ws.length === 0) {
      workspaceStorageService.createWorkspace(userId, "Không gian cá nhân");
    }
  },
};
