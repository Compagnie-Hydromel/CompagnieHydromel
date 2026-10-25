import { useTranslation } from "react-i18next";
import LanguageSelection from "./language-selection";

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-black bg-opacity-70 text-center py-4">
      <p className="text-sm text-gray-300">
        {new Date().getFullYear()} &copy; {t("home.name")}.{" "}
        {t("generic.all_rights_reserved")}
      </p>
      <LanguageSelection />
    </footer>
  );
};

export default Footer;
