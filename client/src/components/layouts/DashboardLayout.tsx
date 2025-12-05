import { Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

import { useAppSelector } from '@/store/hooks';
import { Navbar } from '@/components/dashboard/Navbar';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { AlertSound } from '@/components/dashboard/AlertSound';

export function DashboardLayout() {
  const { sidebarCollapsed } = useAppSelector((state) => state.ui);

  return (
    <div className="min-h-screen bg-background">
      {/* Alert Sound Component */}
      <AlertSound />

      {/* Navbar */}
      <Navbar />

      <div className="flex pt-16">
        {/* Sidebar */}
        <AnimatePresence mode="wait">
          {!sidebarCollapsed && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="hidden lg:block"
            >
              <Sidebar />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <main
          className={`flex-1 transition-all duration-200 ${
            sidebarCollapsed ? 'lg:ml-0' : 'lg:ml-0'
          }`}
        >
          <div className="h-[calc(100vh-4rem)] overflow-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

