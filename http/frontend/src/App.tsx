import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import Home from "./pages/home";
import NotFoundPage from "./pages/404";
import Dashboard from "./pages/dashboard";
import MusicPage from "./pages/dashboard/music";
import DashboardLayout from "./pages/dashboard/layout";
import "./i18n";
import Profile from "./pages/dashboard/profile";
import AdminLayout from "./pages/dashboard/admin/layout";
import AdminLayouts from "./pages/dashboard/admin/layouts";
import AdminWallpapers from "./pages/dashboard/admin/wallpapers";
import AdminMembers from "./pages/dashboard/admin/members";
import AdminRoles from "./pages/dashboard/admin/roles";
import AdminBanner from "./pages/dashboard/admin/banner";
import AdminMessages from "./pages/dashboard/admin/messages";
import SuperadminBadges from "./pages/dashboard/superadmin/badges";
import SuperadminRadios from "./pages/dashboard/superadmin/radios";
import SuperadminLayout from "./pages/dashboard/superadmin/layout";
import SuperadminUsers from "./pages/dashboard/superadmin/users";
import SuperadminUserDetail from "./pages/dashboard/superadmin/user-detail";

function App() {
  return (
    <Router>
      <Routes>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="music" element={<MusicPage />} />
          <Route path="profile" element={<Profile />} />
          <Route path="superadmin" element={<SuperadminLayout />}>
            <Route index element={<Navigate to="users" replace />} />
            <Route path="users" element={<SuperadminUsers />} />
            <Route path="users/:userId" element={<SuperadminUserDetail />} />
            <Route path="badges" element={<SuperadminBadges />} />
            <Route path="radios" element={<SuperadminRadios />} />
          </Route>
          <Route path="admin" element={<AdminLayout />}>
            <Route path="messages" element={<AdminMessages />} />
            <Route path="banner" element={<AdminBanner />} />
            <Route path="roles" element={<AdminRoles />} />
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
