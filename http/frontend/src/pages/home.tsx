import React from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelection from '../components/language-selection';

const Home: React.FC = () => {
    const { t } = useTranslation();

    return (
        <>
            <header className="flex flex-col items-center justify-center min-h-screen text-white">
                <h1 className="text-6xl font-extrabold mb-6 drop-shadow-lg">
                    {t("home.welcome_to")} <span className="text-yellow-300">{t("home.name")}</span>
                </h1>
                <p className="text-2xl mb-8 max-w-lg text-center drop-shadow-md">
                    {t("home.description")}
                </p>
            </header>
            <div className="bg-black bg-opacity-70 p-8 mx-4 my-8 rounded-lg max-w-4xl mx-auto">
                <h2 className="text-3xl font-semibold mb-4">{t("home.about_us.title")}</h2>
                <p className="mb-4">
                    {t("home.about_us.paragraph1")}
                </p>
                <p>
                    {t("home.about_us.paragraph2")}
                </p>
            </div>

            <section className="bg-yellow-300 text-black p-8 mx-4 my-8 rounded-lg max-w-4xl mx-auto text-center">
                <h2 className="text-3xl font-semibold mb-4">{t("home.join_our_discord.title")}</h2>
                <p className="mb-4">
                    {t("home.join_our_discord.description")}
                </p>
                <div
                    className="flex flex-col sm:flex-row justify-center gap-4"
                >
                    <a
                        href="https://discord.com/users/338972372260618241"
                        target='_blank'
                        className="inline-block px-6 py-3 bg-black text-yellow-300 font-bold rounded-lg shadow-md hover:bg-gray-800 transition"
                    >
                        Cirth, {t("home.roles.owner")}
                    </a>
                    <a
                        href="https://discord.com/users/386200134628671492"
                        target='_blank'
                        className="inline-block px-6 py-3 bg-black text-yellow-300 font-bold rounded-lg shadow-md hover:bg-gray-800 transition"
                    >
                        Ethann69, {t("home.roles.developer")}
                    </a>
                </div>
            </section>

            <footer className="bg-black bg-opacity-70 text-center py-4">
                <p className="text-sm text-gray-300">
                    {new Date().getFullYear()}  &copy; {t("home.name")}. {t("generic.all_rights_reserved")}
                </p>
                <LanguageSelection />
            </footer>
        </>
    );
};

export default Home;