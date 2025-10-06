import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { User } from '../../models/user';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import GuildSelection from '../../components/guild-selection';
import React from 'react';
import { useNavigate } from 'react-router-dom';

const DashboardLayout = () => {
    const navigate = useNavigate();
    const [currentUser, setCurrentUser] = React.useState<User | null>(null);

    useEffect(() => {
        const checkAuth = async () => {
            const user = await User.current();
            if (!user) {
                navigate('/');
            }
            setCurrentUser(user);
        };
        checkAuth();
    }, [navigate]);
    
    return (  
        <>
            <header className="flex justify-between items-center p-4 bg-yellow-300 text-black">
                <GuildSelection guilds={[]} onSelect={(guild) => console.log(guild)} />
                <div className="flex items-center space-x-4">
                    {currentUser && (
                        <div className="flex items-center space-x-2">
                            <img
                                src={currentUser?.get("avatar_url") ?? "https://cdn.discordapp.com/embed/avatars/0.png"}
                                alt="Profile" 
                                className="w-10 h-10 rounded-full"
                            />
                            <span className="text-lg">{currentUser?.get("display_name")}</span>
                        </div>
                    )}
                    <button 
                        onClick={() => {
                            User.logout();
                            navigate('/');
                        }} 
                        className="text-5xl"
                    >
                        <FontAwesomeIcon icon={faRightFromBracket} />
                    </button>
                </div>
            </header>
            <main>
                <Outlet />
            </main>
        </>
    );
};

export default DashboardLayout;
