import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import Home from "./pages/home";
import NotFoundPage from "./pages/404";
import Dashboard from "./pages/dashboard";
import DashboardLayout from "./pages/dashboard/layout";
import "./i18n";
import Profile from "./pages/dashboard/profile";
import AdminLayout from "./pages/dashboard/admin/layout";
import AdminLayouts from "./pages/dashboard/admin/layouts";
import AdminWallpapers from "./pages/dashboard/admin/wallpapers";
import AdminMembers from "./pages/dashboard/admin/members";

function App() {
  return (
    <Router>
      <Routes>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="profile" element={<Profile />} />
          <Route path="admin" element={<AdminLayout />}>
            <Route path="members" element={<AdminMembers />} />
            <Route index element={<Navigate to="layouts" replace />} />
            <Route path="layouts" element={<AdminLayouts />} />
            <Route path="wallpapers" element={<AdminWallpapers />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
}

export default App;
