import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authStorageService } from "@/services/auth.storage";
import { workspaceStorageService } from "@/services/workspace.storage";

interface WorkspaceCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function WorkspaceCreateDialog({
  open,
  onOpenChange,
}: WorkspaceCreateDialogProps) {
  const [workspaceName, setWorkspaceName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleCreate = () => {
    // 1. Kiểm tra đầu vào
    if (!workspaceName.trim()) {
      alert("Vui lòng nhập tên không gian làm việc!");
      return;
    }

    setIsLoading(true);

    try {
      // 2. Lấy thông tin user hiện tại
      const user = authStorageService.getCurrentUser();
      if (!user || !user.id) {
        alert("Bạn chưa đăng nhập!");
        return;
      }

      // 3. Gọi Service để tạo workspace mới
      const newWorkspace = workspaceStorageService.createWorkspace(
        user.id,
        workspaceName,
      );

      console.log("Đã tạo workspace mới:", newWorkspace);

      // 4. Reset form và đóng dialog
      setWorkspaceName("");
      onOpenChange(false);

      // Lưu ý: Logic cập nhật danh sách bên Sidebar sẽ tự chạy
      // nhờ vào hàm onOpenChange chúng ta đã xử lý bên AppSidebar.tsx
    } catch (error) {
      console.error("Lỗi khi tạo workspace:", error);
      alert("Có lỗi xảy ra, vui lòng thử lại.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Tạo không gian làm việc mới</DialogTitle>
          <DialogDescription>
            Tạo không gian riêng cho đội nhóm hoặc dự án của bạn. Bạn sẽ là quản
            trị viên.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Tên
            </Label>
            <Input
              id="name"
              placeholder="Ví dụ: Team Marketing, Dự án A..."
              className="col-span-3"
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              // Bấm Enter cũng tạo luôn cho tiện
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreate();
              }}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Hủy
          </Button>
          <Button onClick={handleCreate} disabled={isLoading}>
            {isLoading ? "Đang tạo..." : "Tạo mới"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
