import { motion } from "framer-motion";

/**
 * Simplified therapy animation with static brain illustration
 * Features: Smaller orb, minimal animation, clean design
 */
const TherapyAnimation = () => {
  return (
    <div className="relative w-[240px] h-[240px] flex items-center justify-center">
      {/* Main orb - smaller and subtle */}
      <motion.div
        className="absolute w-48 h-48 rounded-full"
        style={{
          background: "radial-gradient(circle at 30% 30%, rgba(241, 90, 42, 0.15), rgba(241, 90, 42, 0.08))",
          boxShadow: "0 0 30px rgba(241, 90, 42, 0.1)",
        }}
        animate={{
          scale: [1, 1.03, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Static Brain Illustration */}
      <svg
        className="absolute"
        width="100"
        height="100"
        viewBox="0 0 100 100"
        fill="none"
      >
        {/* Brain outline */}
        <path
          d="M50 20C58 20 65 23 70 28C75 33 78 40 78 48C78 56 75 63 70 68C65 73 58 76 50 76C42 76 35 73 30 68C25 63 22 56 22 48C22 40 25 33 30 28C35 23 42 20 50 20Z"
          fill="#F15A2A"
          fillOpacity="0.15"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
        />

        {/* Brain convolutions - left hemisphere */}
        <path
          d="M35 35C35 35 38 32 42 33C46 34 48 38 48 42"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M30 45C30 45 33 42 37 43C41 44 43 48 43 52"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M33 55C33 55 36 52 40 53C44 54 46 58 46 62"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />

        {/* Brain convolutions - right hemisphere */}
        <path
          d="M65 35C65 35 62 32 58 33C54 34 52 38 52 42"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M70 45C70 45 67 42 63 43C59 44 57 48 57 52"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M67 55C67 55 64 52 60 53C56 54 54 58 54 62"
          stroke="#F15A2A"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
        />

        {/* Center division */}
        <path
          d="M50 25 L50 70"
          stroke="#F15A2A"
          strokeWidth="1"
          strokeLinecap="round"
          strokeDasharray="3 3"
          opacity="0.4"
        />
      </svg>

      {/* Subtle outer glow */}
      <div
        className="absolute inset-0 rounded-full blur-2xl -z-10"
        style={{
          background: "radial-gradient(circle, rgba(241, 90, 42, 0.08), transparent 70%)",
        }}
      />
    </div>
  );
};

export default TherapyAnimation;
