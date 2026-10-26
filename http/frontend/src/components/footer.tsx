import { useTranslation } from "react-i18next";
import LanguageSelection from "./language-selection";

const projectLinks = [
  {
    href: "https://github.com/Compagnie-Hydromel/CompagnieHydromel",
    label: "footer.github",
  },
  {
    href: "https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki",
    label: "footer.wiki",
  },
  {
    href: "https://github.com/Compagnie-Hydromel/CompagnieHydromel/issues",
    label: "footer.issues",
  },
];

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-black bg-opacity-70 text-center py-4">
      <p className="text-sm text-gray-300">
        {new Date().getFullYear()} &copy; {t("home.name")}.{" "}
        {t("generic.all_rights_reserved")}
      </p>
      <nav
        aria-label={t("footer.links")}
        className="my-3 flex flex-wrap justify-center gap-x-6 gap-y-2 px-4 text-sm text-gray-300"
      >
        {projectLinks.map(({ href, label }) => (
          <a
            key={href}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-sm underline-offset-4 hover:text-white hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-amber-400"
          >
            {t(label)}
          </a>
        ))}
      </nav>
      <LanguageSelection />
    </footer>
  );
};

export default Footer;
