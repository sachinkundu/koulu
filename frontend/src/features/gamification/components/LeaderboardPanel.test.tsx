import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LeaderboardPanel } from './LeaderboardPanel';
import type { LeaderboardEntry } from '../types';

const mockEntries: LeaderboardEntry[] = [
  { rank: 1, user_id: 'u1', display_name: 'Alice', avatar_url: null, level: 3, points: 15 },
  { rank: 2, user_id: 'u2', display_name: 'Bob', avatar_url: null, level: 2, points: 12 },
  { rank: 3, user_id: 'u3', display_name: 'Carol', avatar_url: null, level: 2, points: 9 },
];

const mockYourRank: LeaderboardEntry = {
  rank: 12,
  user_id: 'u-me',
  display_name: 'Me',
  avatar_url: null,
  level: 1,
  points: 2,
};

describe('LeaderboardPanel', () => {
  it('renders header title', () => {
    render(
      <LeaderboardPanel title="Leaderboard (7-day)" entries={mockEntries} yourRank={null} period="7day" />,
    );
    expect(screen.getByText('Leaderboard (7-day)')).toBeInTheDocument();
  });

  it('renders correct number of rows', () => {
    render(
      <LeaderboardPanel title="Test" entries={mockEntries} yourRank={null} period="7day" />,
    );
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('Carol')).toBeInTheDocument();
  });

  it('shows YourRankSection when yourRank is provided', () => {
    render(
      <LeaderboardPanel title="Test" entries={mockEntries} yourRank={mockYourRank} period="7day" />,
    );
    expect(screen.getByText('Your rank')).toBeInTheDocument();
    expect(screen.getByText('Me')).toBeInTheDocument();
  });

  it('hides YourRankSection when yourRank is null', () => {
    render(
      <LeaderboardPanel title="Test" entries={mockEntries} yourRank={null} period="7day" />,
    );
    expect(screen.queryByText('Your rank')).not.toBeInTheDocument();
  });

  it('shows empty message when no entries', () => {
    render(
      <LeaderboardPanel title="Test" entries={[]} yourRank={null} period="7day" />,
    );
    expect(screen.getByText(/No rankings yet/)).toBeInTheDocument();
  });

  it('shows error message on error', () => {
    render(
      <LeaderboardPanel
        title="Test"
        entries={[]}
        yourRank={null}
        period="7day"
        error={new Error('fail')}
      />,
    );
    expect(screen.getByText('Failed to load leaderboard.')).toBeInTheDocument();
  });

  it('shows skeleton during loading', () => {
    const { container } = render(
      <LeaderboardPanel title="Test" entries={[]} yourRank={null} period="7day" isLoading />,
    );
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
