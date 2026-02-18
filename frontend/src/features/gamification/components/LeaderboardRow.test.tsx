import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LeaderboardRow } from './LeaderboardRow';
import type { LeaderboardEntry } from '../types';

const mockEntry: LeaderboardEntry = {
  rank: 1,
  user_id: 'user-1',
  display_name: 'Alice Admin',
  avatar_url: null,
  level: 3,
  points: 15,
};

describe('LeaderboardRow', () => {
  it('renders medal for top 3 ranks', () => {
    render(<LeaderboardRow entry={mockEntry} period="7day" />);
    expect(screen.getByRole('img', { name: 'Gold medal' })).toBeInTheDocument();
  });

  it('renders rank number for rank 4+', () => {
    const entry = { ...mockEntry, rank: 4 };
    render(<LeaderboardRow entry={entry} period="7day" />);
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('shows + prefix for period boards', () => {
    render(<LeaderboardRow entry={mockEntry} period="7day" />);
    expect(screen.getByText('+15')).toBeInTheDocument();
  });

  it('shows no prefix for all-time', () => {
    render(<LeaderboardRow entry={mockEntry} period="alltime" />);
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('applies highlight class when highlight is true', () => {
    const { container } = render(<LeaderboardRow entry={mockEntry} period="7day" highlight />);
    expect(container.firstChild).toHaveClass('bg-blue-50');
  });

  it('renders display name', () => {
    render(<LeaderboardRow entry={mockEntry} period="7day" />);
    expect(screen.getByText('Alice Admin')).toBeInTheDocument();
  });
});
