import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import TherapyAnimation from "../components/ui/therapy-animation";
import { cn } from "../lib/utils";
import HelpDrawer from "../components/HelpDrawer";
import safespaceLogo from "../assets/safespace_logo.png";

const defaultAnimationConfig = {
  positions: [
    { top: "50%", left: "75%", scale: 1.4 },  // Hero: Right side, balanced
    { top: "25%", left: "50%", scale: 0.9 },  // Clients: Top center, subtle
    { top: "15%", left: "20%", scale: 2 },    // Therapists: Left side, larger
    { top: "50%", left: "50%", scale: 1.8 },  // Community: Center, large backdrop
  ]
};

const lerp = (start, end, factor) => {
  return start + (end - start) * factor;
};

const parsePercent = (str) => parseFloat(str.replace('%', ''));

function ScrollTherapy({ sections, animationConfig = defaultAnimationConfig, className }) {
  const [activeSection, setActiveSection] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [animationTransform, setAnimationTransform] = useState("");
  const containerRef = useRef(null);
  const sectionRefs = useRef([]);
  const animationFrameId = useRef();
  const navLabelTimeoutRef = useRef();

  const calculatedPositions = useMemo(() => {
    return animationConfig.positions.map(pos => ({
      top: parsePercent(pos.top),
      left: parsePercent(pos.left),
      scale: pos.scale
    }));
  }, [animationConfig.positions]);

  const updateScrollPosition = useCallback(() => {
    const scrollTop = window.pageYOffset;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = Math.min(Math.max(scrollTop / docHeight, 0), 1);

    setScrollProgress(progress);

    const viewportCenter = window.innerHeight / 2;
    let newActiveSection = 0;
    let minDistance = Infinity;

    sectionRefs.current.forEach((ref, index) => {
      if (ref) {
        const rect = ref.getBoundingClientRect();
        const sectionCenter = rect.top + rect.height / 2;
        const distance = Math.abs(sectionCenter - viewportCenter);

        if (distance < minDistance) {
          minDistance = distance;
          newActiveSection = index;
        }
      }
    });

    const currentPos = calculatedPositions[newActiveSection];
    const transform = `translate3d(${currentPos.left}vw, ${currentPos.top}vh, 0) translate3d(-50%, -50%, 0) scale3d(${currentPos.scale}, ${currentPos.scale}, 1)`;

    setAnimationTransform(transform);
    setActiveSection(newActiveSection);
  }, [calculatedPositions]);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        animationFrameId.current = requestAnimationFrame(() => {
          updateScrollPosition();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    updateScrollPosition();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
      if (navLabelTimeoutRef.current) {
        clearTimeout(navLabelTimeoutRef.current);
      }
    };
  }, [updateScrollPosition]);

  useEffect(() => {
    const initialPos = calculatedPositions[0];
    const initialTransform = `translate3d(${initialPos.left}vw, ${initialPos.top}vh, 0) translate3d(-50%, -50%, 0) scale3d(${initialPos.scale}, ${initialPos.scale}, 1)`;
    setAnimationTransform(initialTransform);
  }, [calculatedPositions]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative w-full max-w-screen overflow-x-hidden min-h-screen",
        className
      )}
      style={{
        fontFamily: "'Inter', sans-serif",
        background: '#F7F3EC'
      }}
    >
      {/* Navigation Header */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
        className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
        style={{ boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)' }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16 sm:h-20">
            <Link to="/" className="flex items-center">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center"
                style={{ gap: '0.125rem' }}
              >
                <img 
                  src={safespaceLogo} 
                  alt="SafeSpace" 
                  className="h-14 sm:h-16 md:h-20 w-auto object-contain"
                  style={{ maxWidth: '220px' }}
                />
                <span 
                  className="text-2xl sm:text-3xl md:text-4xl font-bold hidden sm:inline-block" 
                  style={{ 
                    fontFamily: "'Inter', sans-serif", 
                    background: 'linear-gradient(135deg, #111827 0%, #1F2937 50%, #374151 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    color: 'transparent',
                    fontWeight: 800,
                    letterSpacing: '-0.05em',
                    lineHeight: '1',
                    textRendering: 'optimizeLegibility',
                    WebkitFontSmoothing: 'antialiased',
                    MozOsxFontSmoothing: 'grayscale'
                  }}
                >
                  SafeSpace
                </span>
              </motion.div>
            </Link>
            <div className="flex items-center gap-3 sm:gap-4">
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-medium rounded-lg transition-colors hover:bg-gray-100/50"
                style={{ 
                  fontFamily: "'Inter', sans-serif", 
                  color: '#3F3F3F',
                  fontWeight: 500
                }}
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm font-semibold rounded-lg transition-all hover:shadow-lg"
                style={{ 
                  fontFamily: "'Inter', sans-serif", 
                  background: '#F15A2A',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px -2px rgba(241, 90, 42, 0.3)'
                }}
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Progress Bar - Solid orange */}
      <div className="fixed top-16 sm:top-20 left-0 w-full h-1 bg-gray-200/30 z-40">
        <div
          className="h-full will-change-transform"
          style={{
            background: '#F15A2A',
            transform: `scaleX(${scrollProgress})`,
            transformOrigin: 'left center',
            transition: 'transform 0.15s ease-out',
          }}
        />
      </div>

      {/* Navigation Dots - Red theme */}
      <div className="hidden sm:flex fixed right-2 sm:right-4 lg:right-8 top-1/2 -translate-y-1/2 z-40">
        <div className="space-y-3 sm:space-y-4 lg:space-y-6">
          {sections.map((section, index) => (
            <div key={index} className="relative group">
              <div
                className={cn(
                  "nav-label absolute right-5 sm:right-6 lg:right-8 top-1/2 -translate-y-1/2",
                  "px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2 rounded-md sm:rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap",
                  "bg-white/95 backdrop-blur-md border border-gray-200 shadow-xl z-50",
                  activeSection === index ? "animate-fadeOut" : "opacity-0"
                )}
              >
                <div className="flex items-center gap-1 sm:gap-1.5 lg:gap-2">
                  <div className="w-1 sm:w-1.5 lg:w-2 h-1 sm:h-1.5 lg:h-2 rounded-full" style={{ background: '#F15A2A' }} />
                  <span className="text-xs sm:text-sm lg:text-base" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500, color: '#3F3F3F' }}>
                    {section.badge || `Section ${index + 1}`}
                  </span>
                </div>
              </div>

              <button
                onClick={() => {
                  sectionRefs.current[index]?.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                  });
                }}
                className={cn(
                  "relative w-2 h-2 sm:w-2.5 sm:h-2.5 lg:w-3 lg:h-3 rounded-full border-2 transition-all duration-300 hover:scale-125"
                )}
                style={activeSection === index ? {
                  background: '#F15A2A',
                  borderColor: '#F15A2A',
                  boxShadow: '0 4px 6px -1px rgba(241, 90, 42, 0.3)'
                } : {
                  background: 'transparent',
                  borderColor: 'rgba(156, 163, 175, 0.4)'
                }}
                aria-label={`Go to ${section.badge || `section ${index + 1}`}`}
              />
            </div>
          ))}
        </div>

        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 lg:w-px bg-gradient-to-b from-transparent via-gray-300/20 to-transparent -translate-x-1/2 -z-10" />
      </div>

      {/* Therapy Animation */}
      <div
        className="fixed z-10 pointer-events-none will-change-transform transition-all duration-[1400ms] ease-[cubic-bezier(0.23,1,0.32,1)]"
        style={{
          transform: animationTransform,
          filter: `opacity(${activeSection === 3 ? 0.4 : 0.85})`,
        }}
      >
        <div className="scale-75 sm:scale-90 lg:scale-100">
          <TherapyAnimation />
        </div>
      </div>

      {/* Dynamic sections */}
      {sections.map((section, index) => (
        <section
          key={section.id}
          ref={(el) => (sectionRefs.current[index] = el)}
          className={cn(
            "relative min-h-screen flex flex-col justify-center px-4 sm:px-6 md:px-8 lg:px-12 z-20 py-12 sm:py-16 lg:py-20",
            "w-full max-w-full overflow-hidden",
            section.align === 'center' && "items-center text-center",
            section.align === 'right' && "items-end text-right",
            section.align !== 'center' && section.align !== 'right' && "items-start text-left"
          )}
        >
          <div className={cn(
            "w-full max-w-sm sm:max-w-lg md:max-w-2xl lg:max-w-4xl xl:max-w-5xl will-change-transform transition-all duration-700",
            "opacity-100 translate-y-0"
          )}>

            <h1 className={cn(
              "font-bold mb-6 sm:mb-8 leading-[1.1] tracking-tight",
              index === 0
                ? "text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl"
                : "text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl"
            )}
            style={{ fontFamily: "'Inter', sans-serif", fontWeight: 800, color: '#3F3F3F' }}>
              {section.subtitle ? (
                <div className="space-y-1 sm:space-y-2">
                  <div>
                    {section.title}
                  </div>
                  <div style={{ fontSize: '0.6em', fontWeight: 600, color: '#3F3F3F', opacity: 0.7, letterSpacing: '0.05em' }}>
                    {section.subtitle}
                  </div>
                </div>
              ) : (
                <div>
                  {section.title}
                </div>
              )}
            </h1>

            <div className={cn(
              "leading-relaxed mb-8 sm:mb-10 text-base sm:text-lg lg:text-xl",
              section.align === 'center' ? "max-w-full mx-auto text-center" : "max-w-full"
            )}
            style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400, color: '#3F3F3F', opacity: 0.8 }}>
              <p className="mb-3 sm:mb-4">{section.description}</p>
              {index === 0 && (
                <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 text-xs sm:text-sm mt-4 sm:mt-6"
                  style={{ color: '#3F3F3F', opacity: 0.6 }}>
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div className="w-1 h-1 rounded-full" style={{ background: '#F15A2A' }} />
                    <span>Interactive Experience</span>
                  </div>
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div className="w-1 h-1 rounded-full" style={{ background: '#F15A2A' }} />
                    <span>Scroll to Explore</span>
                  </div>
                </div>
              )}
            </div>

            {/* Features with Advanced Animations */}
            {section.features && (
              <div className={cn(
                "mb-8 sm:mb-10",
                section.id === 'therapists'
                  ? "flex justify-center"
                  : ""
              )}>
                <div className={cn(
                  section.id === 'therapists'
                    ? "grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 max-w-5xl"
                    : "grid gap-3 sm:gap-4"
                )}>
                {section.features.map((feature, featureIndex) => {
                  // Define icons for each feature
                  const getIcon = () => {
                    if (feature.title.includes('Confidential')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      );
                    } else if (feature.title.includes('Licensed')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                      );
                    } else if (feature.title.includes('Flexible')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      );
                    } else if (feature.title.includes('Streamlined')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                      );
                    } else if (feature.title.includes('Secure')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                      );
                    } else if (feature.title.includes('AI-Assisted')) {
                      return (
                        <svg className="w-12 h-12 sm:w-14 sm:h-14" fill="none" stroke="#F15A2A" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      );
                    }
                    return null;
                  };

                  return (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{
                      duration: 0.6,
                      delay: featureIndex * 0.15,
                      ease: [0.23, 1, 0.32, 1]
                    }}
                    whileHover={{
                      y: -12,
                      scale: 1.02,
                      transition: { duration: 0.3, ease: "easeOut" }
                    }}
                    className={cn(
                      "group relative p-5 sm:p-6 lg:p-7 rounded-2xl border border-gray-200/80 bg-white shadow-sm",
                      "transition-all duration-500 cursor-pointer overflow-hidden",
                      section.id === 'therapists' && "min-h-[280px] flex flex-col justify-center"
                    )}
                    style={{
                      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
                    }}
                  >
                    {/* Top Accent Line */}
                    <motion.div
                      className="absolute top-0 left-0 right-0 h-1"
                      style={{
                        background: '#F15A2A',
                        transformOrigin: 'left'
                      }}
                      initial={{ scaleX: 0 }}
                      whileHover={{ scaleX: 1 }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                    />

                    {/* Subtle overlay */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{
                        background: 'rgba(241, 90, 42, 0.05)'
                      }}
                    />

                    {/* Shimmer effect */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100"
                      initial={{ x: '-100%' }}
                      whileHover={{ x: '100%' }}
                      transition={{ duration: 0.8, ease: "easeInOut" }}
                      style={{
                        background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)',
                      }}
                    />

                    {/* Enhanced shadow on hover */}
                    <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"
                      style={{
                        boxShadow: '0 20px 50px -12px rgba(241, 90, 42, 0.15)'
                      }}
                    />

                    <div className={cn(
                      "flex flex-col items-center text-center relative z-10",
                      section.id === 'therapists' ? "space-y-3 sm:space-y-4" : "flex-row items-start gap-3 sm:gap-4"
                    )}>
                      {/* Icon */}
                      {section.id !== 'therapists' && (
                        <div className="flex-shrink-0">
                          {getIcon()}
                        </div>
                      )}

                      <div className={cn(
                        "space-y-1.5 sm:space-y-2",
                        section.id === 'therapists' ? "w-full" : "flex-1 min-w-0"
                      )}>
                        {/* Icon for therapists section (centered on top) */}
                        {section.id === 'therapists' && (
                          <div className="flex justify-center mb-3">
                            {getIcon()}
                          </div>
                        )}

                        <motion.h3
                          className={cn(
                            "font-bold text-base sm:text-lg transition-colors duration-300",
                            section.id === 'therapists' && "text-center"
                          )}
                          style={{ fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
                          whileHover={{ color: '#F15A2A' }}
                          transition={{ duration: 0.2 }}
                        >
                          {feature.title}
                        </motion.h3>
                        <p className={cn(
                          "leading-relaxed text-sm sm:text-base transition-colors duration-300",
                          section.id === 'therapists' && "text-center"
                        )}
                          style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400, color: '#3F3F3F', opacity: 0.8 }}>
                          {feature.description}
                        </p>
                      </div>

                      {/* Corner accent */}
                      <motion.div
                        className="absolute top-0 right-0 w-20 h-20 opacity-0 group-hover:opacity-100"
                        initial={{ scale: 0, rotate: 0 }}
                        whileHover={{ scale: 1, rotate: 45 }}
                        transition={{ duration: 0.4 }}
                        style={{
                          background: 'radial-gradient(circle at top right, rgba(241, 90, 42, 0.08), transparent 60%)',
                          borderTopRightRadius: '1rem'
                        }}
                      />
                    </div>

                    {/* Bottom shadow gradient */}
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-1 opacity-0 group-hover:opacity-100 blur-sm"
                      style={{
                        background: 'rgba(241, 90, 42, 0.3)',
                      }}
                      initial={{ opacity: 0 }}
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.5 }}
                    />
                  </motion.div>
                  );
                })}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            {section.actions && (
              <div className={cn(
                "flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4",
                section.align === 'center' && "justify-center",
                section.align === 'right' && "justify-end",
                (!section.align || section.align === 'left') && "justify-start"
              )}>
                {section.actions.map((action, actionIndex) => (
                  <motion.div
                    key={action.label}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{
                      duration: 0.5,
                      delay: actionIndex * 0.1 + 0.2,
                      ease: [0.23, 1, 0.32, 1]
                    }}
                    className="w-full sm:w-auto"
                  >
                    <Link
                      to={action.to}
                      className={cn(
                        "group relative px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-semibold transition-all duration-300 text-sm sm:text-base",
                        "focus:outline-none w-full sm:w-auto text-center inline-block overflow-hidden",
                        action.variant === 'primary'
                          ? "shadow-lg"
                          : "border-2 border-gray-300 bg-white/80 backdrop-blur-sm hover:bg-gray-50 hover:border-gray-400"
                      )}
                      style={action.variant === 'primary' ? {
                        background: '#F15A2A',
                        color: '#FFFFFF',
                        boxShadow: '0 10px 25px -5px rgba(241, 90, 42, 0.3)',
                        fontFamily: "'Inter', sans-serif",
                        fontWeight: 600
                      } : {
                        fontFamily: "'Inter', sans-serif",
                        fontWeight: 600,
                        color: '#3F3F3F'
                      }}
                      onMouseEnter={(e) => {
                        if (action.variant === 'primary') {
                          e.currentTarget.style.transform = 'translateY(-2px)';
                          e.currentTarget.style.boxShadow = '0 20px 40px -10px rgba(241, 90, 42, 0.4)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (action.variant === 'primary') {
                          e.currentTarget.style.transform = 'translateY(0)';
                          e.currentTarget.style.boxShadow = '0 10px 25px -5px rgba(241, 90, 42, 0.3)';
                        }
                      }}
                    >
                      <span className="relative z-10">{action.label}</span>
                    </Link>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </section>
      ))}
    </div>
  );
}

export default function Landing() {
  const therapySections = [
    {
      id: "hero",
      badge: "Welcome",
      title: "Find Your Path to Wellness",
      subtitle: "Professional Therapy, Accessible to Everyone",
      description: "Connect with licensed therapists or grow your practice on our secure, compassionate platform. Your journey to mental wellness starts here, in a safe space designed for healing and growth.",
      align: "left",
      actions: [
        { label: "I'm Seeking Therapy", variant: "primary", to: "/register" },
        { label: "I'm a Therapist", variant: "primary", to: "/professional/register" },
        { label: "Sign In", variant: "secondary", to: "/login" },
      ]
    },
    {
      id: "clients",
      badge: "For Clients",
      title: "Your Journey to Better Mental Health",
      description: "Experience compassionate, professional therapy from the comfort of your home. Our platform connects you with licensed therapists who understand your unique needs and provide personalized support.",
      align: "center",
      features: [
        {
          title: "Confidential Sessions",
          description: "100% private and secure journaling and chat sessions with end-to-end encryption. Your mental health journey is yours alone."
        },
        {
          title: "Licensed Professionals",
          description: "Connect with verified, experienced therapists specialized in various areas including anxiety, depression, trauma, and relationships."
        },
        {
          title: "Flexible Support",
          description: "Access AI-powered journaling insights and supportive chat whenever you need it. Get help on your schedule, at your pace."
        }
      ]
    },
    {
      id: "therapists",
      badge: "For Therapists",
      title: "Grow Your Practice, Help More People",
      description: "Join a community of mental health professionals making a real difference. Our platform provides the tools you need to focus on what matters most—supporting your clients on their healing journey.",
      align: "left",
      features: [
        {
          title: "Streamlined Client Management",
          description: "Intuitive dashboard to review client journals, track progress, and manage your caseload efficiently. All your client data in one secure place."
        },
        {
          title: "Secure Platform",
          description: "HIPAA-compliant infrastructure with end-to-end encryption. Protect your clients' privacy while delivering exceptional care."
        },
        {
          title: "AI-Assisted Insights",
          description: "Leverage AI-powered analysis to identify key themes and emotions in client journals, helping you provide more targeted support."
        }
      ]
    },
    {
      id: "community",
      badge: "Together",
      title: "Healing Starts Here",
      description: "Join thousands who have found their path to wellness with SafeSpace. Whether you're seeking support or providing it, you're part of a community dedicated to mental health, healing, and wellbeing. Together, we create a safer space for everyone.",
      align: "center",
      actions: [
        { label: "Start Your Journey", variant: "primary", to: "/register" },
        { label: "Join as a Therapist", variant: "secondary", to: "/professional/register" }
      ]
    }
  ];

  return (
    <>
      <ScrollTherapy
        sections={therapySections}
      />
      <HelpDrawer />
    </>
  );
}
