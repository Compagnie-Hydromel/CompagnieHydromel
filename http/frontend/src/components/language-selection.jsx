import { useTranslation } from "react-i18next";

const LanguageSelection = () => {
    const supportedLanguages = ['en', 'fr'];
    const { i18n } = useTranslation();

    return (
        <select name="language" id="language-select" onClick={ (e) => {
            const lang = e.target.value;
            localStorage.setItem('language', lang);
            i18n.changeLanguage(lang);
        }} className="ml-4 bg-black bg-opacity-50 text-gray-300 p-2 rounded">
            {supportedLanguages.map((lang) => (
                <option key={lang} value={lang} selected={i18n.language === lang}>
                    {lang.toUpperCase()}
                </option>
            ))}
        </select>
    );
}

export default LanguageSelection;
