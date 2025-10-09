import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
    const { t } = useTranslation();
    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <h1 className="text-6xl font-extrabold drop-shadow-lg text-yellow-300">404</h1>
            <h2 className="text-2xl font-semibold mt-4">{t("not_found.title")}</h2>
            <p className="mt-2 text-lg">
                {t("not_found.message")}
            </p>
            <Link
                to="/"
                className="mt-6 px-6 py-3 bg-white font-bold rounded-lg shadow-md hover:bg-gray-100 transition text-black"
            >
                {t("not_found.go_home")}
            </Link>
        </div>
    );
};

export default NotFoundPage;