import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { User } from '../../models/user';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRightFromBracket } from '@fortawesome/free-solid-svg-icons';

const DashboardLayout = () => {
    useEffect(() => {
        const checkAuth = async () => {
            const user = await User.current();
            if (!user) {
                window.location.href = '/';
            }
        };
        checkAuth();
    }, []);
    
    return (  
        <>
            <header className="relative">
                <button 
                    onClick={() => {
                        User.logout();
                        window.location.href = '/';
                    }} 
                    className="text-5xl absolute right-4 top-4"
                >
                    <FontAwesomeIcon icon={faRightFromBracket} />
                </button>
            </header>
            <main>
                <Outlet />
            </main>
        </>
    );
};

export default DashboardLayout;
