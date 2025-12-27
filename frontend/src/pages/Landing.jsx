import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import TherapyAnimation from "../components/ui/therapy-animation";
import { cn } from "../lib/utils";

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
        "relative w-full max-w-screen overflow-x-hidden min-h-screen text-gray-900",
        className
      )}
      style={{
        background: 'linear-gradient(to bottom right, #f5f3ff, #e0e7ff, #dbeafe, #d1fae5)'
      }}
    >
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-0.5 bg-gradient-to-r from-purple-200/20 via-blue-200/40 to-green-200/20 z-50">
        <div
          className="h-full will-change-transform shadow-sm"
          style={{
            background: 'linear-gradient(to right, #667eea, #4facfe, #00f2fe)',
            transform: `scaleX(${scrollProgress})`,
            transformOrigin: 'left center',
            transition: 'transform 0.15s ease-out',
            filter: 'drop-shadow(0 0 2px rgba(102, 126, 234, 0.3))'
          }}
        />
      </div>

      {/* Navigation Dots */}
      <div className="hidden sm:flex fixed right-2 sm:right-4 lg:right-8 top-1/2 -translate-y-1/2 z-40">
        <div className="space-y-3 sm:space-y-4 lg:space-y-6">
          {sections.map((section, index) => (
            <div key={index} className="relative group">
              <div
                className={cn(
                  "nav-label absolute right-5 sm:right-6 lg:right-8 top-1/2 -translate-y-1/2",
                  "px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2 rounded-md sm:rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap",
                  "bg-white/95 backdrop-blur-md border border-purple-200/60 shadow-xl z-50",
                  activeSection === index ? "animate-fadeOut" : "opacity-0"
                )}
              >
                <div className="flex items-center gap-1 sm:gap-1.5 lg:gap-2">
                  <div className="w-1 sm:w-1.5 lg:w-2 h-1 sm:h-1.5 lg:h-2 rounded-full bg-purple-500 animate-pulse" />
                  <span className="text-xs sm:text-sm lg:text-base">
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
                  "relative w-2 h-2 sm:w-2.5 sm:h-2.5 lg:w-3 lg:h-3 rounded-full border-2 transition-all duration-300 hover:scale-125",
                  "before:absolute before:inset-0 before:rounded-full before:transition-all before:duration-300",
                  activeSection === index
                    ? "bg-purple-500 border-purple-500 shadow-lg before:animate-ping before:bg-purple-500/20"
                    : "bg-transparent border-gray-400/40 hover:border-purple-500/60 hover:bg-purple-500/10"
                )}
                aria-label={`Go to ${section.badge || `section ${index + 1}`}`}
              />
            </div>
          ))}
        </div>

        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 lg:w-px bg-gradient-to-b from-transparent via-purple-300/20 to-transparent -translate-x-1/2 -z-10" />
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
            )}>
              {section.subtitle ? (
                <div className="space-y-1 sm:space-y-2">
                  <div className="gradient-text">
                    {section.title}
                  </div>
                  <div className="text-gray-600/90 text-[0.6em] sm:text-[0.7em] font-medium tracking-wider">
                    {section.subtitle}
                  </div>
                </div>
              ) : (
                <div className="gradient-text">
                  {section.title}
                </div>
              )}
            </h1>

            <div className={cn(
              "text-gray-700/80 leading-relaxed mb-8 sm:mb-10 text-base sm:text-lg lg:text-xl font-light",
              section.align === 'center' ? "max-w-full mx-auto text-center" : "max-w-full"
            )}>
              <p className="mb-3 sm:mb-4">{section.description}</p>
              {index === 0 && (
                <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 text-xs sm:text-sm text-gray-600/60 mt-4 sm:mt-6">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div className="w-1 h-1 rounded-full bg-purple-500 animate-pulse" />
                    <span>Interactive Experience</span>
                  </div>
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div className="w-1 h-1 rounded-full bg-purple-500 animate-pulse" style={{ animationDelay: '0.5s' }} />
                    <span>Scroll to Explore</span>
                  </div>
                </div>
              )}
            </div>

            {/* Features */}
            {section.features && (
              <div className="grid gap-3 sm:gap-4 mb-8 sm:mb-10">
                {section.features.map((feature, featureIndex) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{
                      duration: 0.5,
                      delay: featureIndex * 0.1,
                      ease: [0.23, 1, 0.32, 1]
                    }}
                    whileHover={{
                      y: -8,
                      scale: 1.02,
                      transition: { duration: 0.3, ease: "easeOut" }
                    }}
                    className={cn(
                      "group relative p-4 sm:p-5 lg:p-6 rounded-lg sm:rounded-xl border border-purple-200/60 bg-white/50 backdrop-blur-sm",
                      "transition-all duration-500 cursor-pointer overflow-hidden"
                    )}
                  >
                    {/* Animated gradient background overlay */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{
                        background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, rgba(139, 92, 246, 0.15) 50%, rgba(79, 172, 254, 0.1) 100%)'
                      }}
                    />

                    {/* Shimmer effect on hover */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100"
                      initial={{ x: '-100%' }}
                      whileHover={{ x: '100%' }}
                      transition={{ duration: 0.8, ease: "easeInOut" }}
                      style={{
                        background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)',
                      }}
                    />

                    {/* Enhanced shadow layers */}
                    <div className="absolute inset-0 rounded-lg sm:rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"
                      style={{
                        boxShadow: '0 20px 50px -12px rgba(139, 92, 246, 0.25), 0 0 0 1px rgba(167, 139, 250, 0.1)'
                      }}
                    />

                    <div className="flex items-start gap-3 sm:gap-4 relative z-10">
                      {/* Animated icon/dot with pulse effect */}
                      <motion.div
                        className="relative mt-1.5 sm:mt-2 flex-shrink-0"
                        whileHover={{ scale: 1.3, rotate: 180 }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                      >
                        <div className="w-3 sm:w-4 h-3 sm:h-4 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 shadow-lg" />
                        <motion.div
                          className="absolute inset-0 rounded-full bg-purple-400"
                          animate={{
                            scale: [1, 1.5, 1],
                            opacity: [0.5, 0, 0.5]
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut"
                          }}
                        />
                      </motion.div>

                      <div className="flex-1 space-y-1.5 sm:space-y-2 min-w-0">
                        <motion.h3
                          className="font-semibold text-gray-900 text-base sm:text-lg group-hover:text-purple-700 transition-colors duration-300"
                          whileHover={{ x: 4 }}
                          transition={{ duration: 0.2 }}
                        >
                          {feature.title}
                        </motion.h3>
                        <p className="text-gray-700/80 leading-relaxed text-sm sm:text-base group-hover:text-gray-900 transition-colors duration-300">
                          {feature.description}
                        </p>
                      </div>

                      {/* Animated corner accent */}
                      <motion.div
                        className="absolute top-0 right-0 w-16 h-16 opacity-0 group-hover:opacity-100"
                        initial={{ scale: 0, rotate: 0 }}
                        whileHover={{ scale: 1, rotate: 45 }}
                        transition={{ duration: 0.4 }}
                        style={{
                          background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.1), transparent)',
                          borderTopRightRadius: '0.75rem'
                        }}
                      />
                    </div>

                    {/* Bottom gradient border accent */}
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100"
                      initial={{ scaleX: 0 }}
                      whileHover={{ scaleX: 1 }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      style={{
                        background: 'linear-gradient(90deg, #a78bfa, #8b5cf6, #4facfe)',
                        transformOrigin: 'left'
                      }}
                    />
                  </motion.div>
                ))}
              </div>
            )}

            {/* Actions */}
            {section.actions && (
              <div className={cn(
                "flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4",
                section.align === 'center' && "justify-center",
                section.align === 'right' && "justify-end",
                (!section.align || section.align === 'left') && "justify-start"
              )}>
                {section.actions.map((action, actionIndex) => (
                  <Link
                    key={action.label}
                    to={action.to}
                    className={cn(
                      "group relative px-6 sm:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl font-medium transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] text-sm sm:text-base",
                      "hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-500/20 w-full sm:w-auto text-center",
                      action.variant === 'primary'
                        ? "btn-primary text-white shadow-lg"
                        : "border-2 border-purple-200/60 bg-white/50 backdrop-blur-sm hover:bg-purple-50/50 hover:border-purple-300/30 text-gray-900"
                    )}
                    style={{ animationDelay: `${actionIndex * 0.1 + 0.2}s` }}
                  >
                    <span className="relative z-10">{action.label}</span>
                  </Link>
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
    <ScrollTherapy
      sections={therapySections}
    />
  );
}
