import React from "react";
import { motion } from "framer-motion";

/**
 * Calming therapy-themed animation component
 * Features: Breathing circle, floating peaceful elements, gentle gradients
 */
const TherapyAnimation = () => {
  return (
    <div className="relative w-[300px] h-[300px] flex items-center justify-center">
      {/* Main breathing circle - represents mindfulness and calm */}
      <motion.div
        className="absolute w-48 h-48 rounded-full"
        style={{
          background: "radial-gradient(circle at 30% 30%, rgba(147, 197, 253, 0.6), rgba(196, 181, 253, 0.4), rgba(167, 243, 208, 0.3))",
          boxShadow: "0 0 60px rgba(147, 197, 253, 0.4), 0 0 120px rgba(196, 181, 253, 0.2)",
        }}
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.6, 0.8, 0.6],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Inner glow circle */}
      <motion.div
        className="absolute w-32 h-32 rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(255, 255, 255, 0.8), rgba(147, 197, 253, 0.4))",
          boxShadow: "0 0 40px rgba(255, 255, 255, 0.6)",
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.7, 1, 0.7],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.5,
        }}
      />

      {/* Floating peaceful elements - leaves/petals */}
      {[0, 1, 2, 3, 4, 5].map((index) => (
        <motion.div
          key={index}
          className="absolute w-3 h-3 rounded-full"
          style={{
            background: `rgba(${index % 2 === 0 ? '147, 197, 253' : '167, 243, 208'}, 0.6)`,
            left: `${50 + Math.cos((index * Math.PI) / 3) * 40}%`,
            top: `${50 + Math.sin((index * Math.PI) / 3) * 40}%`,
            boxShadow: "0 0 15px rgba(147, 197, 253, 0.4)",
          }}
          animate={{
            y: [0, -20, 0],
            x: [0, Math.cos(index) * 10, 0],
            opacity: [0.4, 0.8, 0.4],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 3 + index * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.3,
          }}
        />
      ))}

      {/* Orbiting calm elements */}
      {[0, 1, 2].map((index) => (
        <motion.div
          key={`orbit-${index}`}
          className="absolute w-2 h-2 rounded-full"
          style={{
            background: "rgba(196, 181, 253, 0.7)",
            boxShadow: "0 0 10px rgba(196, 181, 253, 0.5)",
          }}
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 15 + index * 5,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          <div
            className="w-2 h-2 rounded-full"
            style={{
              position: "absolute",
              left: `${80 + index * 20}px`,
              background: "rgba(167, 243, 208, 0.6)",
              boxShadow: "0 0 8px rgba(167, 243, 208, 0.4)",
            }}
          />
        </motion.div>
      ))}

      {/* Gentle wave rings */}
      {[0, 1, 2, 3].map((index) => (
        <motion.div
          key={`ring-${index}`}
          className="absolute rounded-full border-2"
          style={{
            width: `${120 + index * 30}px`,
            height: `${120 + index * 30}px`,
            borderColor: `rgba(147, 197, 253, ${0.3 - index * 0.06})`,
          }}
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.5, 0.2, 0.5],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.4,
          }}
        />
      ))}

      {/* Center peace symbol - subtle heart pulse */}
      <motion.div
        className="absolute text-4xl"
        style={{
          filter: "drop-shadow(0 0 10px rgba(147, 197, 253, 0.6))",
        }}
        animate={{
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <span className="text-blue-300/80">✨</span>
      </motion.div>

      {/* Ambient background glow */}
      <div
        className="absolute inset-0 rounded-full blur-3xl -z-10"
        style={{
          background: "radial-gradient(circle, rgba(147, 197, 253, 0.2), rgba(196, 181, 253, 0.15), transparent)",
        }}
      />
    </div>
  );
};

export default TherapyAnimation;
