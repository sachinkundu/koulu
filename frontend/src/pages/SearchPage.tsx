import { useAuth } from '@/features/identity/hooks';
import { SearchResults } from '@/features/search/components';
import { TabBar, UserDropdown } from '@/components';
import { SearchBar } from '@/features/search/components/SearchBar';

const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
  { label: 'Members', path: '/members' },
];

export function SearchPage(): JSX.Element {
  const { user, logout, isLoading } = useAuth();
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-gray-900">Koulu</h1>
            <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
              {projectName}
            </span>
          </div>
          {user !== null && <SearchBar />}
          {user !== null && (
            <div className="flex items-center space-x-4">
              <UserDropdown user={user} onLogout={() => void logout()} />
            </div>
          )}
        </div>
      </header>
      <TabBar tabs={APP_TABS} />
      <SearchResults />
    </div>
  );
}
