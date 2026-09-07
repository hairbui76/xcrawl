// Vitest smoke test for the placeholder shell.

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import App, { NAV_ENTRIES } from './App';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe('App shell', () => {
  it('renders exactly the five primary navigation entries of SRC-SPEC §4', () => {
    renderAt('/reports');
    const links = screen.getAllByRole('link');
    expect(links.map((link) => link.textContent)).toEqual([
      'Reports',
      'Topics',
      'Saved',
      'Runs',
      'Settings',
    ]);
  });

  it('defaults to Reports (D45)', () => {
    renderAt('/');
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Reports');
  });

  it.each(NAV_ENTRIES)('routes $path to a placeholder for $screen', ({ path, label }) => {
    renderAt(path);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(label);
  });
});
