import { Route, BrowserRouter as Router, Routes } from "react-router-dom"
import Home from "./pages/home"
import NotFoundPage from "./pages/404"

function App() {
  return (
    <Router>
      <Routes>
        <Route index element={<Home />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App
