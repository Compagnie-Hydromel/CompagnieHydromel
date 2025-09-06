import React from 'react';

const Home: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 text-white">
            <h1 className="text-5xl font-extrabold mb-6 drop-shadow-lg">
                Welcome to <span className="text-yellow-300">Compagnie Hydromel</span>
            </h1>
            <p className="text-xl mb-8 max-w-lg text-center drop-shadow-md">
                The best community and discord server. 🍺
            </p>
        </div>
    );
};

export default Home;