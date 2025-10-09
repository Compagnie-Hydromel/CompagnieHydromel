import { Route, BrowserRouter as Router, Routes } from "react-router-dom"
import Home from "./pages/home"
import NotFoundPage from "./pages/404"
import Dashboard from "./pages/dashboard"
import DashboardLayout from "./pages/dashboard/layout"
import "./i18n";

function App() {
  return (
    <Router>
      <Routes>
        <Route index element={<Home />} />
        <Route path="dashboard" element={
          <DashboardLayout />
        }>
          <Route index element={<Dashboard />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App
