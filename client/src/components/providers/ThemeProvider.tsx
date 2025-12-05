import { useEffect, ReactNode } from "react";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { updateSystemTheme } from "@/store/slices/themeSlice";

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const dispatch = useAppDispatch();
  const { mode, resolvedMode } = useAppSelector((state) => state.theme);

  useEffect(() => {
    // Apply theme class to document
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(resolvedMode);
  }, [resolvedMode]);

  useEffect(() => {
    // Listen for system theme changes
    if (mode === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

      const handleChange = () => {
        dispatch(updateSystemTheme());
      };

      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    }
  }, [mode, dispatch]);

  return <>{children}</>;
}
