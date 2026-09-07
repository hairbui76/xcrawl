// Placeholder application shell.
//
// It renders the five primary navigation entries of SRC-SPEC §4 — "Điều hướng chính:
// Reports · Topics · Saved · Runs · Settings" — as routes, and nothing else. Reports is
// the default screen (D45), so `/` redirects to it.
//
// There is NO data here, and that is deliberate: every screen's read model belongs to the
// card that owns it (`web/src/routes/*.ts`, `web/src/views/*.tsx` in
// agent-tasks/README.md §5.3). A placeholder that fetched something would be a second,
// un-reviewed implementation of a read model.

import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';

/** The five entries of SRC-SPEC §4, in the order the spec lists them. */
export const NAV_ENTRIES = [
  { path: '/reports', label: 'Reports', screen: 'SCR-reports' },
  { path: '/topics', label: 'Topics', screen: 'SCR-topics' },
  { path: '/saved', label: 'Saved', screen: 'SCR-saved' },
  { path: '/runs', label: 'Runs', screen: 'SCR-runs' },
  { path: '/settings', label: 'Settings', screen: 'SCR-settings' },
] as const;

function Placeholder({ label, screen }: { label: string; screen: string }) {
  return (
    <section aria-labelledby="screen-heading">
      <h1 id="screen-heading">{label}</h1>
      <p>
        Màn hình <code>{screen}</code> chưa được hiện thực. Read model và view của nó thuộc card
        triển khai tương ứng.
      </p>
    </section>
  );
}

export function Navigation() {
  const { pathname } = useLocation();
  return (
    <nav aria-label="Điều hướng chính">
      <ul>
        {NAV_ENTRIES.map((entry) => (
          <li key={entry.path}>
            <Link to={entry.path} aria-current={pathname === entry.path ? 'page' : undefined}>
              {entry.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default function App() {
  return (
    <>
      <Navigation />
      <main>
        <Routes>
          {/* Reports is the default screen (D45). */}
          <Route path="/" element={<Navigate to="/reports" replace />} />
          {NAV_ENTRIES.map((entry) => (
            <Route
              key={entry.path}
              path={entry.path}
              element={<Placeholder label={entry.label} screen={entry.screen} />}
            />
          ))}
          <Route path="*" element={<p>Không có màn hình nào ở đường dẫn này.</p>} />
        </Routes>
      </main>
    </>
  );
}
