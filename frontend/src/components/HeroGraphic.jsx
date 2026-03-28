/**
 * Simple professional hero illustration for the home page (uses theme accent blue).
 */
export default function HeroGraphic() {
  return (
    <div className="hero-graphic-wrap" aria-hidden="true">
      <svg className="hero-graphic" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
        {/* Soft base */}
        <rect
          className="hero-graphic__base"
          x="24"
          y="32"
          width="352"
          height="136"
          rx="20"
        />
        {/* Abstract “growth / skyline” — minimal bars */}
        <rect className="hero-graphic__bar" x="88" y="108" width="36" height="52" rx="6" />
        <rect className="hero-graphic__bar hero-graphic__bar--mid" x="148" y="84" width="36" height="76" rx="6" />
        <rect className="hero-graphic__bar hero-graphic__bar--tall" x="208" y="64" width="36" height="96" rx="6" />
        <rect className="hero-graphic__bar" x="268" y="96" width="36" height="64" rx="6" />
        {/* Horizon / connection line */}
        <path
          className="hero-graphic__line"
          d="M 72 164 L 328 164"
          fill="none"
          strokeWidth="2"
          strokeLinecap="round"
        />
        {/* Hub node */}
        <circle className="hero-graphic__hub" cx="200" cy="52" r="14" />
        <circle className="hero-graphic__hub-ring" cx="200" cy="52" r="22" fill="none" strokeWidth="1.5" />
      </svg>
    </div>
  );
}
