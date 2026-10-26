import React from "react";
import { User } from "../models/user";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export const Profile: React.FC<{ currentUser: User | null }> = ({
  currentUser,
}) => {
  const { t } = useTranslation();
  const [hideDropdown, setHideDropdown] = React.useState(true);
  const navigate = useNavigate();

  return (
    <div className="header-profile flex items-center justify-end">
      {currentUser && (
        <div className="relative">
          <button
            type="button"
            className="flex items-center cursor-pointer rounded-full"
            aria-label={t("generic.account")}
            aria-expanded={!hideDropdown}
            aria-controls="account-dropdown"
            onClick={() => setHideDropdown(!hideDropdown)}
            onKeyDown={(event) => {
              if (event.key === "Escape") setHideDropdown(true);
            }}
          >
            <img
              src={
                currentUser?.get("avatar_url") ??
                "https://cdn.discordapp.com/embed/avatars/0.png"
              }
              alt="Profile"
              className="header-avatar rounded-full"
            />
          </button>
          <div
            id="account-dropdown"
            className="absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded shadow-lg"
            hidden={hideDropdown}
          >
            <div className="px-4 py-2 font-bold border-b border-gray-300">
              {currentUser?.get("display_name") ?? "Unknown User"}
            </div>
            <ul className="py-2">
              <li>
                <button
                  type="button"
                  className="w-full text-left px-4 py-3 hover:bg-gray-100 cursor-pointer"
                  onClick={async () => {
                    await User.logout();
                    navigate("/");
                  }}
                >
                  {t("generic.logout")}
                </button>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
