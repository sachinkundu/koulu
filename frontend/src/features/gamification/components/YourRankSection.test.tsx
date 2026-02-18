import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { YourRankSection } from './YourRankSection';
import type { LeaderboardEntry } from '../types';

const mockEntry: LeaderboardEntry = {
  rank: 12,
  user_id: 'user-12',
  display_name: 'Test User',
  avatar_url: null,
  level: 1,
  points: 3,
};

describe('YourRankSection', () => {
  it('renders "Your rank" label', () => {
    render(<YourRankSection entry={mockEntry} period="7day" />);
    expect(screen.getByText('Your rank')).toBeInTheDocument();
  });

  it('renders a highlighted LeaderboardRow', () => {
    const { container } = render(<YourRankSection entry={mockEntry} period="7day" />);
    const row = container.querySelector('.bg-blue-50');
    expect(row).toBeInTheDocument();
  });

  it('renders the display name', () => {
    render(<YourRankSection entry={mockEntry} period="7day" />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });
});
