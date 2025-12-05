import { NavLink, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Map,
  BarChart3,
  Bell,
  Settings,
  User,
  ChevronRight,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAppSelector } from "@/store/hooks";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Map View",
    href: "/map",
    icon: Map,
  },
  {
    title: "Analysis",
    href: "/analysis",
    icon: BarChart3,
  },
  {
    title: "Alerts",
    href: "/alerts",
    icon: Bell,
  },
];

const bottomNavItems = [
  {
    title: "Profile",
    href: "/profile",
    icon: User,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export function Sidebar() {
  const location = useLocation();
  const { unacknowledgedAlerts } = useAppSelector((state) => state.alerts);

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-[280px] border-r bg-background/95 backdrop-blur z-40"
    >
      <div className="flex h-full flex-col justify-between p-4">
        {/* Main Navigation */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-accent",
                  isActive
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="flex-1">{item.title}</span>
                {item.href === "/alerts" && unacknowledgedAlerts.length > 0 && (
                  <span
                    className={cn(
                      "flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-xs font-medium",
                      isActive
                        ? "bg-primary-foreground/20 text-primary-foreground"
                        : "bg-destructive text-destructive-foreground"
                    )}
                  >
                    {unacknowledgedAlerts.length}
                  </span>
                )}
                {isActive && <ChevronRight className="h-4 w-4" />}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Navigation */}
        <nav className="space-y-1 border-t pt-4">
          {bottomNavItems.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;

            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-accent",
                  isActive
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="flex-1">{item.title}</span>
                {isActive && <ChevronRight className="h-4 w-4" />}
              </NavLink>
            );
          })}
        </nav>
      </div>
    </motion.aside>
  );
}
