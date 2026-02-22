import { NavLink } from 'react-router-dom';

export default function NavItem({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-2 rounded-lg text-sm 
        ${isActive ? 'bg-blue-500 text-white' : 'hover:bg-[var(--bg-color)]'}`
      }
    >
      <span>{icon}</span>
      {label}
    </NavLink>
  );
}