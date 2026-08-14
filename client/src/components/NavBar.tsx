import { useState } from "react";
import { NavLink } from "react-router-dom";
import "./NavBar.css";

type LinkItem = { to: string; label: string };

// Links to display in the navigation bar. Customize this array to add or remove links.
const defaultLinks: LinkItem[] = [
  { to: "/", label: "Home" },
  { to: "/product", label: "Product" },
];

export default function NavBar({
  links = defaultLinks,
}: {
  links?: LinkItem[];
}) {
  const [open, setOpen] = useState(false);
  return (
    <nav className={`nav ${open ? "nav-open" : ""}`}>
      <div className="nav-container">
        <div className="nav-brand"></div>

        <button
          className="nav-hamburger"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle navigation"
        >
          <span />
          <span />
          <span />
        </button>

        <ul className={`nav-links ${open ? "show" : ""}`}>
          {links.map((l) => (
            <li key={l.to}>
              <NavLink
                to={l.to}
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                onClick={() => setOpen(false)}
              >
                {l.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
