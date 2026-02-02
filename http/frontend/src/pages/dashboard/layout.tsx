import { Outlet } from "react-router-dom";
import { Header } from "../../components/header";

const DashboardLayout = () => {
  return (
    <>
      <Header />
      <main>
        <Outlet />
      </main>
    </>
  );
};

export default DashboardLayout;
