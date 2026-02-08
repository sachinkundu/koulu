import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Avatar } from './Avatar';
import type { User } from '@/features/identity/types';

interface UserDropdownProps {
  user: User;
  onLogout: () => void;
}

export function UserDropdown({ user, onLogout }: UserDropdownProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (dropdownRef.current !== null && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Avatar button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-full"
        data-testid="user-avatar-button"
      >
        <Avatar
          src={user.profile?.avatar_url}
          alt={user.profile?.display_name ?? user.email}
          fallback={user.profile?.display_name ?? user.email}
          size="md"
        />
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 z-50"
          data-testid="user-dropdown-menu"
        >
          <div className="py-1">
            {/* Email */}
            <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-200">
              {user.email}
            </div>

            {/* Profile link */}
            <Link
              to={`/profile/${user.id}`}
              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setIsOpen(false)}
              data-testid="dropdown-profile-link"
            >
              Profile
            </Link>

            {/* Edit Profile link */}
            <Link
              to="/profile/edit"
              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setIsOpen(false)}
              data-testid="dropdown-edit-profile-link"
            >
              Edit Profile
            </Link>

            {/* Logout button */}
            <button
              onClick={() => {
                setIsOpen(false);
                onLogout();
              }}
              className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 border-t border-gray-200"
              data-testid="dropdown-logout-button"
            >
              Log out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
