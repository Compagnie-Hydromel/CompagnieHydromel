import React from "react";
import { User } from "../models/user";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export const Profile: React.FC<{ currentUser: User | null }> = ({ currentUser }) => {
  const { t } = useTranslation();
  const [hideDropdown, setHideDropdown] = React.useState(true);
  const navigate = useNavigate();

  return (
    <div className="flex items-center space-x-4 w-40 justify-end">
      {currentUser && (
        <div className="relative">
          <div className="flex items-center space-x-2 cursor-pointer">
            <img
              onClick={() => {
                setHideDropdown(!hideDropdown);
              }}
              src={
                currentUser?.get("avatar_url") ??
                "https://cdn.discordapp.com/embed/avatars/0.png"
              }
              alt="Profile"
              className="w-20 h-20 rounded-full"
            />
          </div>
          <div
            className="absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded shadow-lg"
            hidden={hideDropdown}
          >
            <div className="px-4 py-2 font-bold border-b border-gray-300">
              {currentUser?.get("display_name") ?? "Unknown User"}
            </div>
            <ul className="py-2">
              <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">
                {t("generic.settings")}
              </li>
              <li
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={async () => {
                  await User.logout();
                  navigate("/");
                }}
              >
                {t("generic.logout")}
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
