/**
 * Profile sidebar component showing user info and social links.
 */

import { Link } from 'react-router-dom';
import { ProfileLevelSection } from '@/features/gamification/components/ProfileLevelSection';
import type { ProfileDetail } from '../types';

interface LevelInfo {
  level: number;
  levelName: string;
  totalPoints: number;
  pointsToNextLevel: number | null;
  isMaxLevel: boolean;
}

interface ProfileSidebarProps {
  profile: ProfileDetail;
  levelInfo?: LevelInfo;
}

function formatLocation(city: string | null, country: string | null): string | null {
  if (city !== null && country !== null) return `${city}, ${country}`;
  if (city !== null) return city;
  if (country !== null) return country;
  return null;
}

export function ProfileSidebar({ profile, levelInfo }: ProfileSidebarProps): JSX.Element {
  const location = formatLocation(profile.location_city, profile.location_country);

  return (
    <aside className="rounded-lg bg-white p-6 shadow" data-testid="profile-sidebar">
      {/* Avatar */}
      <div className="flex flex-col items-center">
        {profile.avatar_url !== null ? (
          <img
            src={profile.avatar_url}
            alt={profile.display_name ?? 'User avatar'}
            className="h-24 w-24 rounded-full object-cover"
            data-testid="profile-avatar"
          />
        ) : (
          <div
            className="flex h-24 w-24 items-center justify-center rounded-full bg-gray-200 text-3xl font-bold text-gray-500"
            data-testid="profile-avatar-placeholder"
          >
            {profile.display_name?.charAt(0).toUpperCase() ?? '?'}
          </div>
        )}

        {/* Display name */}
        <h1
          className="mt-4 text-xl font-bold text-gray-900"
          data-testid="profile-display-name"
        >
          {profile.display_name ?? 'Anonymous'}
        </h1>

        {/* Bio */}
        {profile.bio !== null && (
          <p className="mt-2 text-center text-sm text-gray-600" data-testid="profile-bio">
            {profile.bio}
          </p>
        )}

        {/* Location */}
        {location !== null && (
          <p className="mt-2 text-sm text-gray-500" data-testid="profile-location">
            {location}
          </p>
        )}
      </div>

      {/* Level info */}
      {levelInfo !== undefined && (
        <ProfileLevelSection
          level={levelInfo.level}
          levelName={levelInfo.levelName}
          totalPoints={levelInfo.totalPoints}
          pointsToNextLevel={levelInfo.pointsToNextLevel}
          isMaxLevel={levelInfo.isMaxLevel}
        />
      )}

      {/* Social links */}
      <SocialLinks profile={profile} />

      {/* Edit button */}
      {profile.is_own_profile && (
        <div className="mt-6">
          <Link
            to="/profile/edit"
            className="block w-full rounded-md border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-700 hover:bg-gray-50"
            data-testid="profile-edit-button"
          >
            Edit Profile
          </Link>
        </div>
      )}
    </aside>
  );
}

function SocialLinks({ profile }: { profile: ProfileDetail }): JSX.Element | null {
  const links = [
    { url: profile.twitter_url, label: 'Twitter' },
    { url: profile.linkedin_url, label: 'LinkedIn' },
    { url: profile.instagram_url, label: 'Instagram' },
    { url: profile.website_url, label: 'Website' },
  ].filter((link) => link.url !== null);

  if (links.length === 0) return null;

  return (
    <div className="mt-4 space-y-2" data-testid="profile-social-links">
      {links.map((link) => (
        <a
          key={link.label}
          href={link.url as string}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-sm text-blue-600 hover:underline"
          data-testid={`profile-social-${link.label.toLowerCase()}`}
        >
          {link.label}
        </a>
      ))}
    </div>
  );
}
