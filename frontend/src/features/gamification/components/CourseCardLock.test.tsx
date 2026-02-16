import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { CourseCardLock } from './CourseCardLock';

describe('CourseCardLock', () => {
  it('renders lock overlay when user level is below requirement', () => {
    render(
      <CourseCardLock
        minimumLevel={3}
        minimumLevelName="Builder"
        currentLevel={1}
      />,
    );
    expect(screen.getByText('Unlock at Level 3')).toBeInTheDocument();
    expect(screen.getByText('Builder')).toBeInTheDocument();
  });

  it('renders nothing when user meets level requirement', () => {
    const { container } = render(
      <CourseCardLock
        minimumLevel={3}
        minimumLevelName="Builder"
        currentLevel={3}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when user exceeds level requirement', () => {
    const { container } = render(
      <CourseCardLock
        minimumLevel={3}
        minimumLevelName="Builder"
        currentLevel={5}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('shows lock icon', () => {
    render(
      <CourseCardLock
        minimumLevel={5}
        minimumLevelName="Mentor"
        currentLevel={2}
      />,
    );
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});
