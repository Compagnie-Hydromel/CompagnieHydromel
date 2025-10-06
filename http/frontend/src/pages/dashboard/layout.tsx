import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { User } from '../../models/user';
import GuildSelection from '../../components/guild-selection';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Guild } from '../../models/guild';

const DashboardLayout = () => {
    const navigate = useNavigate();
    const [currentUser, setCurrentUser] = React.useState<User | null>(null);
    const [hideDropdown, setHideDropdown] = React.useState(true);
    const [guilds, setGuilds] = React.useState<Guild[]>([]);

    useEffect(() => {
        const checkAuth = async () => {
            const user = await User.current();
            if (!user) {
                navigate('/');
            }
            setCurrentUser(user);
            setGuilds(await user?.guilds() || []);
        };
        checkAuth();
    }, [navigate]);
    
    return (  
        <>
            <header className="flex justify-between items-center p-4 bg-yellow-300 text-black">
                <GuildSelection guilds={guilds} onSelect={(guild) => console.log(guild)} />
                <div className="flex items-center space-x-4">
                    {currentUser && (
                        <div className="relative">
                            <div className="flex items-center space-x-2 cursor-pointer">
                                <img
                                    onClick={() => {
                                        setHideDropdown(!hideDropdown);
                                    }}
                                    src={currentUser?.get("avatar_url") ?? "https://cdn.discordapp.com/embed/avatars/0.png"}
                                    alt="Profile" 
                                    className="w-20 h-20 rounded-full"
                                />
                            </div>
                            <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded shadow-lg" hidden={hideDropdown}>
                                <div className="px-4 py-2 font-bold border-b border-gray-300">
                                    {currentUser?.get("display_name") ?? "Unknown User"}                                        
                                </div>
                                <ul className="py-2">
                                    <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">
                                        Settings
                                    </li>
                                    <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer" onClick={async () => {
                                        await User.logout();
                                        navigate('/');
                                    }}>
                                        Logout
                                    </li>
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </header>
            <main>
                <Outlet />
            </main>
        </>
    );
};

export default DashboardLayout;
