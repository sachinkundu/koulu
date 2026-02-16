import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { LevelDefinition } from '../types';
import { LevelDefinitionsGrid } from './LevelDefinitionsGrid';

const allLevels: LevelDefinition[] = [
  { level: 1, name: 'Newcomer', threshold: 0, member_percentage: 40.0 },
  { level: 2, name: 'Member', threshold: 100, member_percentage: 20.0 },
  { level: 3, name: 'Builder', threshold: 300, member_percentage: 12.0 },
  { level: 4, name: 'Contributor', threshold: 600, member_percentage: 8.0 },
  { level: 5, name: 'Veteran', threshold: 1000, member_percentage: 6.0 },
  { level: 6, name: 'Expert', threshold: 2000, member_percentage: 5.0 },
  { level: 7, name: 'Leader', threshold: 5000, member_percentage: 4.0 },
  { level: 8, name: 'Champion', threshold: 10000, member_percentage: 3.0 },
  { level: 9, name: 'Legend', threshold: 25000, member_percentage: 2.0 },
];

describe('LevelDefinitionsGrid', () => {
  it('renders all 9 levels', () => {
    render(<LevelDefinitionsGrid levels={allLevels} currentUserLevel={1} />);

    for (let i = 1; i <= 9; i++) {
      expect(screen.getByTestId(`level-card-${i}`)).toBeInTheDocument();
    }
  });

  it('highlights current user level', () => {
    render(<LevelDefinitionsGrid levels={allLevels} currentUserLevel={5} />);

    const currentCard = screen.getByTestId('level-card-5');
    expect(currentCard.className).toContain('border-blue-500');
    expect(currentCard.className).toContain('bg-blue-50');

    const otherCard = screen.getByTestId('level-card-1');
    expect(otherCard.className).not.toContain('border-blue-500');
    expect(otherCard.className).toContain('border-gray-200');
  });

  it('shows member percentages', () => {
    render(<LevelDefinitionsGrid levels={allLevels} currentUserLevel={1} />);

    expect(screen.getByText('40.0% of members')).toBeInTheDocument();
    expect(screen.getByText('2.0% of members')).toBeInTheDocument();
  });

  it('shows level names and thresholds', () => {
    render(<LevelDefinitionsGrid levels={allLevels} currentUserLevel={1} />);

    expect(screen.getByText('Newcomer')).toBeInTheDocument();
    expect(screen.getByText('Legend')).toBeInTheDocument();
    expect(screen.getByText('25,000 points')).toBeInTheDocument();
  });

  it('renders the grid test id', () => {
    render(<LevelDefinitionsGrid levels={allLevels} currentUserLevel={1} />);

    expect(screen.getByTestId('level-definitions-grid')).toBeInTheDocument();
  });
});
