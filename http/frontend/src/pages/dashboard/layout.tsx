import { Outlet } from "react-router-dom";
import { Header } from "../../components/header";
import Footer from "../../components/footer";

const DashboardLayout = () => {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default DashboardLayout;
