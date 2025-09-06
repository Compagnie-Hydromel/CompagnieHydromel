import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-purple-400 via-pink-500 to-red-500 text-white">
            <h1 className="text-6xl font-extrabold drop-shadow-lg">404</h1>
            <h2 className="text-2xl font-semibold mt-4">Page Not Found</h2>
            <p className="mt-2 text-lg text-gray-200">
                Oops! The page you are looking for does not exist.
            </p>
            <Link
                to="/"
                className="mt-6 px-6 py-3 bg-white text-purple-600 font-bold rounded-lg shadow-md hover:bg-gray-100 transition"
            >
                Return to Homepage
            </Link>
        </div>
    );
};

export default NotFoundPage;