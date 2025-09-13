import React from 'react';

const Home: React.FC = () => {
    return (
        <>
            <header className="flex flex-col items-center justify-center min-h-screen text-white">
                <h1 className="text-6xl font-extrabold mb-6 drop-shadow-lg">
                    Welcome to <span className="text-yellow-300">Compagny of Hydromel</span>
                </h1>
                <p className="text-2xl mb-8 max-w-lg text-center drop-shadow-md">
                    The best community and discord server. 🍺
                </p>
            </header>
            <div className="bg-black bg-opacity-70 p-8 mx-4 my-8 rounded-lg max-w-4xl mx-auto">
                <h2 className="text-3xl font-semibold mb-4">About Us</h2>
                <p className="mb-4">
                    The Compagny of Hydromel is your ultimate hangout spot, where fun knows no bounds! Whether you're into epic gaming sessions, groovy tunes, creative masterpieces, or just want to chill with awesome folks, we've got a little something for everyone.
                </p>
                <p>
                    Cheers to new friendships and unforgettable experiences! 🍻
                </p>
            </div>

            <section className="bg-yellow-300 text-black p-8 mx-4 my-8 rounded-lg max-w-4xl mx-auto text-center">
                <h2 className="text-3xl font-semibold mb-4">Join Our Discord Server</h2>
                <p className="mb-4">
                    Want to become a member of our awesome community? You can contact us on Discord!
                </p>
                <div
                    className="flex flex-col sm:flex-row justify-center gap-4"
                >
                    <a
                        href="https://discord.com/users/338972372260618241"
                        target='_blank'
                        className="inline-block px-6 py-3 bg-black text-yellow-300 font-bold rounded-lg shadow-md hover:bg-gray-800 transition"
                    >
                        Cirth, Owner
                    </a>
                    <a
                        href="https://discord.com/users/386200134628671492"
                        target='_blank'
                        className="inline-block px-6 py-3 bg-black text-yellow-300 font-bold rounded-lg shadow-md hover:bg-gray-800 transition"
                    >
                        Ethann69, Developer
                    </a>
                </div>
            </section>

            <footer className="bg-black bg-opacity-70 text-center py-4">
                <p className="text-sm text-gray-300">
                &copy; {new Date().getFullYear()} Compagny of Hydromel. All rights reserved.
                </p>
            </footer>
        </>
    );
};

export default Home;