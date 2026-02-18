import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { RankMedal } from './RankMedal';

describe('RankMedal', () => {
  it('renders gold medal for rank 1', () => {
    render(<RankMedal rank={1} />);
    expect(screen.getByRole('img', { name: 'Gold medal' })).toBeInTheDocument();
  });

  it('renders silver medal for rank 2', () => {
    render(<RankMedal rank={2} />);
    expect(screen.getByRole('img', { name: 'Silver medal' })).toBeInTheDocument();
  });

  it('renders bronze medal for rank 3', () => {
    render(<RankMedal rank={3} />);
    expect(screen.getByRole('img', { name: 'Bronze medal' })).toBeInTheDocument();
  });
});
