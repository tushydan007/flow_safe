import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  CheckCircle,
  Filter,
  Bell,
  MapPin,
  Clock,
  Volume2,
  VolumeX,
} from 'lucide-react';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchAlerts, acknowledgeAlert, toggleSound } from '@/store/slices/alertSlice';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CardSkeleton } from '@/components/common/LoadingSkeleton';
import { cn } from '@/lib/utils';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const severityColors = {
  critical: {
    bg: 'bg-red-50 dark:bg-red-900/10',
    border: 'border-red-200 dark:border-red-900/50',
    text: 'text-red-700 dark:text-red-400',
    icon: 'text-red-500',
  },
  high: {
    bg: 'bg-orange-50 dark:bg-orange-900/10',
    border: 'border-orange-200 dark:border-orange-900/50',
    text: 'text-orange-700 dark:text-orange-400',
    icon: 'text-orange-500',
  },
  medium: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/10',
    border: 'border-yellow-200 dark:border-yellow-900/50',
    text: 'text-yellow-700 dark:text-yellow-400',
    icon: 'text-yellow-500',
  },
  low: {
    bg: 'bg-emerald-50 dark:bg-emerald-900/10',
    border: 'border-emerald-200 dark:border-emerald-900/50',
    text: 'text-emerald-700 dark:text-emerald-400',
    icon: 'text-emerald-500',
  },
};

export function AlertsPage() {
  const dispatch = useAppDispatch();
  const { alerts, severityCounts, isLoading, soundEnabled } = useAppSelector(
    (state) => state.alerts
  );
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [acknowledgedFilter, setAcknowledgedFilter] = useState<string>('unacknowledged');

  useEffect(() => {
    dispatch(fetchAlerts({
      acknowledged: acknowledgedFilter === 'all' ? undefined : acknowledgedFilter === 'acknowledged',
      severity: severityFilter === 'all' ? undefined : severityFilter,
    }));
  }, [dispatch, severityFilter, acknowledgedFilter]);

  const handleAcknowledge = async (alertId: number) => {
    await dispatch(acknowledgeAlert(alertId));
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (severityFilter !== 'all' && alert.severity !== severityFilter) {
      return false;
    }
    if (acknowledgedFilter === 'acknowledged' && !alert.is_acknowledged) {
      return false;
    }
    if (acknowledgedFilter === 'unacknowledged' && alert.is_acknowledged) {
      return false;
    }
    return true;
  });

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alerts</h1>
          <p className="text-muted-foreground">
            Monitor and manage system alerts and notifications
          </p>
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={() => dispatch(toggleSound())}
          className={cn(!soundEnabled && 'text-muted-foreground')}
        >
          {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
        </Button>
      </motion.div>

      {/* Stats */}
      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-4">
        {Object.entries(severityCounts).map(([severity, count]) => {
          const colors = severityColors[severity as keyof typeof severityColors];
          return (
            <div
              key={severity}
              className={cn(
                'rounded-lg border p-4',
                colors?.bg,
                colors?.border
              )}
            >
              <div className="flex items-center justify-between">
                <span className={cn('text-sm font-medium capitalize', colors?.text)}>
                  {severity}
                </span>
                <AlertTriangle className={cn('h-4 w-4', colors?.icon)} />
              </div>
              <p className={cn('text-2xl font-bold mt-1', colors?.text)}>{count}</p>
            </div>
          );
        })}
      </motion.div>

      {/* Filters */}
      <motion.div variants={itemVariants} className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Filters:</span>
        </div>
        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
        <Select value={acknowledgedFilter} onValueChange={setAcknowledgedFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Alerts</SelectItem>
            <SelectItem value="unacknowledged">Unacknowledged</SelectItem>
            <SelectItem value="acknowledged">Acknowledged</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Alerts List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredAlerts.length > 0 ? (
        <motion.div variants={containerVariants} className="space-y-4">
          {filteredAlerts.map((alert) => {
            const colors = severityColors[alert.severity as keyof typeof severityColors];
            return (
              <motion.div
                key={alert.id}
                variants={itemVariants}
                className={cn(
                  'rounded-lg border p-4 transition-all',
                  alert.is_acknowledged
                    ? 'bg-muted/50 opacity-60'
                    : cn(colors?.bg, colors?.border)
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div
                      className={cn(
                        'p-2 rounded-lg',
                        alert.is_acknowledged
                          ? 'bg-muted text-muted-foreground'
                          : colors?.bg
                      )}
                    >
                      <AlertTriangle
                        className={cn('h-5 w-5', !alert.is_acknowledged && colors?.icon)}
                      />
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{alert.title}</h3>
                        <span
                          className={cn(
                            'px-2 py-0.5 rounded-full text-xs font-medium capitalize',
                            colors?.bg,
                            colors?.text
                          )}
                        >
                          {alert.severity}
                        </span>
                        {alert.is_acknowledged && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <CheckCircle className="h-3 w-3" />
                            Acknowledged
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{alert.description}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Bell className="h-3 w-3" />
                          {alert.alert_type_display}
                        </span>
                        {alert.location && (
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {alert.location.lat.toFixed(4)}, {alert.location.lng.toFixed(4)}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  {!alert.is_acknowledged && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      ) : (
        <motion.div
          variants={itemVariants}
          className="text-center py-12 text-muted-foreground"
        >
          <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No alerts matching your filters</p>
        </motion.div>
      )}
    </motion.div>
  );
}

