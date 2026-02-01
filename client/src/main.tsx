import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
// 1. Import Provider
import { GoogleOAuthProvider } from "@react-oauth/google";

// 2. Thay thế bằng Client ID bạn vừa copy ở Bước 1
const GOOGLE_CLIENT_ID =
  "109272703741-mu6n49hnkan1v5db9jsbosib0lj3o36p.apps.googleusercontent.com";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/* 3. Bọc App lại */}
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>,
);
