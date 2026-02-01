import client from "@/lib/axios"; // Import file vừa tạo ở bước trên
import { Project } from "@/types";

export const projectsService = {
  // 1. Lấy danh sách dự án
  getProjects: async (statusFilter?: string) => {
    const response = await client.get("/projects");
    const projects = response.data;

    // Xử lý lọc danh sách nếu cần
    if (statusFilter && statusFilter !== "ALL") {
      return projects.filter((p: Project) => p.status === statusFilter);
    }
    return projects;
  },

  // 2. Lấy chi tiết 1 dự án
  getProjectById: async (id: string) => {
    // Tạm thời lấy hết rồi lọc (vì backend đang dùng list)
    const response = await client.get("/projects");
    return response.data.find((p: Project) => String(p.id) === String(id));
  },

  // 3. Tạo dự án mới
  createProject: async (project: any) => {
    const response = await client.post("/projects", project);
    return response.data;
  },

  // 4. Cập nhật dự án
  updateProject: async (id: string, updates: Partial<Project>) => {
    const response = await client.put(`/projects/${id}`, updates);
    return response.data;
  },

  // 5. Cập nhật trạng thái
  updateStatus: async (id: string, status: "ACTIVE" | "ARCHIVED") => {
    // Giả sử backend nhận update status qua API PUT /projects/{id}
    // Bạn có thể cần điều chỉnh tùy theo API backend thực tế của bạn
    const response = await client.put(`/projects/${id}`, { status });
    return response.data;
  },
};
