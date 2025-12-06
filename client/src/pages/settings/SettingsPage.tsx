import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import {
  Settings,
  Moon,
  Sun,
  Monitor,
  Bell,
  Volume2,
  Mail,
  Loader2,
} from "lucide-react";

import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { fetchSettings, updateSettings } from "@/store/slices/userSlice";
import { setTheme } from "@/store/slices/themeSlice";
import { setSoundEnabled } from "@/store/slices/alertSlice";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ProfileSkeleton } from "@/components/common/LoadingSkeleton";

const settingsSchema = z.object({
  theme: z.enum(["light", "dark", "system"]),
  notifications_enabled: z.boolean(),
  sound_alerts_enabled: z.boolean(),
  email_notifications: z.boolean(),
  map_default_zoom: z.number().min(1).max(18),
  map_default_lat: z.number().min(-90).max(90),
  map_default_lng: z.number().min(-180).max(180),
});

type SettingsFormData = z.infer<typeof settingsSchema>;

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function SettingsPage() {
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { settings, isLoading } = useAppSelector((state) => state.user);

  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { isSubmitting },
  } = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      theme: "system",
      notifications_enabled: true,
      sound_alerts_enabled: true,
      email_notifications: true,
      map_default_zoom: 10,
      map_default_lat: 0,
      map_default_lng: 0,
    },
  });

  // Use useWatch instead of watch() for React Compiler compatibility
  const themeValue = useWatch({ control, name: "theme" });
  const notificationsEnabled = useWatch({
    control,
    name: "notifications_enabled",
  });
  const soundAlertsEnabled = useWatch({
    control,
    name: "sound_alerts_enabled",
  });
  const emailNotifications = useWatch({ control, name: "email_notifications" });

  useEffect(() => {
    dispatch(fetchSettings());
  }, [dispatch]);

  useEffect(() => {
    if (settings) {
      setValue("theme", settings.theme);
      setValue("notifications_enabled", settings.notifications_enabled);
      setValue("sound_alerts_enabled", settings.sound_alerts_enabled);
      setValue("email_notifications", settings.email_notifications);
      setValue("map_default_zoom", settings.map_default_zoom);
      setValue("map_default_lat", settings.map_default_lat);
      setValue("map_default_lng", settings.map_default_lng);
    }
  }, [settings, setValue]);

  const onSubmit = async (data: SettingsFormData) => {
    const result = await dispatch(updateSettings(data));
    if (updateSettings.fulfilled.match(result)) {
      dispatch(setTheme(data.theme));
      dispatch(setSoundEnabled(data.sound_alerts_enabled));
      toast({
        title: "Settings saved",
        description: "Your preferences have been updated successfully.",
        variant: "success",
      });
    } else {
      toast({
        title: "Error",
        description: "Failed to save settings. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleThemeChange = (value: string) => {
    setValue("theme", value as "light" | "dark" | "system");
    dispatch(setTheme(value as "light" | "dark" | "system"));
  };

  if (isLoading && !settings) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <ProfileSkeleton />
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 max-w-2xl mx-auto"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your application preferences
        </p>
      </motion.div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Appearance */}
        <motion.section variants={itemVariants} className="space-y-4">
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-muted-foreground" />
            <h2 className="text-lg font-semibold">Appearance</h2>
          </div>
          <div className="rounded-lg border p-4 space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Theme</Label>
                <p className="text-sm text-muted-foreground">
                  Select your preferred color scheme
                </p>
              </div>
              <Select value={themeValue} onValueChange={handleThemeChange}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">
                    <div className="flex items-center gap-2">
                      <Sun className="h-4 w-4" />
                      Light
                    </div>
                  </SelectItem>
                  <SelectItem value="dark">
                    <div className="flex items-center gap-2">
                      <Moon className="h-4 w-4" />
                      Dark
                    </div>
                  </SelectItem>
                  <SelectItem value="system">
                    <div className="flex items-center gap-2">
                      <Monitor className="h-4 w-4" />
                      System
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </motion.section>

        {/* Notifications */}
        <motion.section variants={itemVariants} className="space-y-4">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-muted-foreground" />
            <h2 className="text-lg font-semibold">Notifications</h2>
          </div>
          <div className="rounded-lg border p-4 space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive in-app notifications
                </p>
              </div>
              <Switch
                checked={notificationsEnabled}
                onCheckedChange={(checked) =>
                  setValue("notifications_enabled", checked)
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="flex items-center gap-2">
                  <Volume2 className="h-4 w-4" />
                  Sound Alerts
                </Label>
                <p className="text-sm text-muted-foreground">
                  Play sound for critical alerts
                </p>
              </div>
              <Switch
                checked={soundAlertsEnabled}
                onCheckedChange={(checked) =>
                  setValue("sound_alerts_enabled", checked)
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Notifications
                </Label>
                <p className="text-sm text-muted-foreground">
                  Receive alerts via email
                </p>
              </div>
              <Switch
                checked={emailNotifications}
                onCheckedChange={(checked) =>
                  setValue("email_notifications", checked)
                }
              />
            </div>
          </div>
        </motion.section>

        {/* Map Defaults */}
        <motion.section variants={itemVariants} className="space-y-4">
          <h2 className="text-lg font-semibold">Map Defaults</h2>
          <div className="rounded-lg border p-4 space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="map_default_zoom">Default Zoom</Label>
                <Input
                  id="map_default_zoom"
                  type="number"
                  min={1}
                  max={18}
                  {...register("map_default_zoom", { valueAsNumber: true })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="map_default_lat">Default Latitude</Label>
                <Input
                  id="map_default_lat"
                  type="number"
                  step="0.000001"
                  {...register("map_default_lat", { valueAsNumber: true })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="map_default_lng">Default Longitude</Label>
                <Input
                  id="map_default_lng"
                  type="number"
                  step="0.000001"
                  {...register("map_default_lng", { valueAsNumber: true })}
                />
              </div>
            </div>
          </div>
        </motion.section>

        {/* Submit */}
        <motion.div variants={itemVariants}>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              "Save Changes"
            )}
          </Button>
        </motion.div>
      </form>
    </motion.div>
  );
}
