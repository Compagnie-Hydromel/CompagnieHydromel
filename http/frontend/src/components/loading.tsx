export default function Loading() {
  return (
    <div className="h-[90vh] items-center justify-center flex">
      <div className="animate-spin">
        <svg
          className="w-24 h-24 text-white"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 100 100"
          fill="none"
        >
          {/* Outer turbine housing */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="currentColor"
            strokeWidth="2"
            opacity="0.5"
          />

          {/* Turbine blades */}
          <g opacity="0.75">
            <path
              d="M 50 50 L 50 15 Q 65 30 70 50"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
            />
            <path
              d="M 50 50 L 85 50 Q 70 65 50 70"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
            />
            <path
              d="M 50 50 L 50 85 Q 35 70 30 50"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
            />
            <path
              d="M 50 50 L 15 50 Q 30 35 50 30"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
            />
          </g>

          {/* Center hub */}
          <circle cx="50" cy="50" r="6" fill="currentColor" opacity="0.7" />
        </svg>
      </div>
    </div>
  );
}
