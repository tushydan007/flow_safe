import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { MapPin } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Panel - Branding */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="hidden lg:flex flex-col justify-between p-12 bg-linear-to-br from-slate-900 via-slate-800 to-slate-900 text-white relative overflow-hidden"
      >
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <svg
            className="w-full h-full"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >
            <defs>
              <pattern
                id="grid"
                width="10"
                height="10"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 10 0 L 0 0 0 10"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid)" />
          </svg>
        </div>

        {/* Animated Circles */}
        <motion.div
          className="absolute top-20 right-20 w-72 h-72 bg-emerald-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{ duration: 8, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-20 left-20 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity }}
        />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="p-2 bg-emerald-500 rounded-xl">
            <MapPin className="w-8 h-8" />
          </div>
          <span className="text-2xl font-bold tracking-tight">GeoMonitor</span>
        </div>

        {/* Content */}
        <div className="relative z-10 space-y-6">
          <h1 className="text-4xl font-bold leading-tight">
            Advanced Pipeline
            <br />
            Monitoring System
          </h1>
          <p className="text-lg text-slate-300 max-w-md">
            Real-time satellite imagery analysis for pipeline infrastructure.
            Detect leaks, monitor facilities, and track changes with AI-powered
            insights.
          </p>

          {/* Features */}
          <div className="grid grid-cols-2 gap-4 pt-4">
            {[
              "Leak Detection",
              "Change Monitoring",
              "Object Detection",
              "Emission Tracking",
            ].map((feature, index) => (
              <motion.div
                key={feature}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-center gap-2 text-slate-300"
              >
                <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                <span className="text-sm">{feature}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10 text-sm text-slate-400">
          © 2024 GeoMonitor. Advanced Geospatial Analytics.
        </div>
      </motion.div>

      {/* Right Panel - Auth Form */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="flex items-center justify-center p-8 bg-background"
      >
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </motion.div>
    </div>
  );
}
