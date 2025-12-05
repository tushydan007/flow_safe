import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Map,
  Satellite,
  AlertTriangle,
  Activity,
  TrendingUp,
  MapPin,
  Clock,
} from 'lucide-react';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchPipelineRoutes } from '@/store/slices/pipelineSlice';
import { fetchSatelliteImages } from '@/store/slices/satelliteSlice';
import { fetchAlerts } from '@/store/slices/alertSlice';
import { CardSkeleton } from '@/components/common/LoadingSkeleton';
import { Button } from '@/components/ui/button';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function DashboardPage() {
  const dispatch = useAppDispatch();
  const { routes, isLoading: pipelineLoading } = useAppSelector((state) => state.pipeline);
  const { images, isLoading: satelliteLoading } = useAppSelector((state) => state.satellite);
  const { alerts, severityCounts, isLoading: alertsLoading } = useAppSelector(
    (state) => state.alerts
  );
  const { user } = useAppSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchPipelineRoutes());
    dispatch(fetchSatelliteImages());
    dispatch(fetchAlerts());
  }, [dispatch]);

  const isLoading = pipelineLoading || satelliteLoading || alertsLoading;

  const stats = [
    {
      title: 'Pipeline Routes',
      value: routes.length,
      icon: MapPin,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      href: '/map',
    },
    {
      title: 'Satellite Images',
      value: images.length,
      icon: Satellite,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
      href: '/analysis',
    },
    {
      title: 'Active Alerts',
      value: alerts.filter((a) => !a.is_acknowledged).length,
      icon: AlertTriangle,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
      href: '/alerts',
    },
    {
      title: 'Analyzed Images',
      value: images.filter((i) => i.is_analyzed).length,
      icon: Activity,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10',
      href: '/analysis',
    },
  ];

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 space-y-8"
    >
      {/* Welcome Section */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.first_name || 'User'}
        </h1>
        <p className="text-muted-foreground">
          Here&apos;s an overview of your pipeline monitoring system
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={containerVariants}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
              className="rounded-xl border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <Link to={stat.href} className="block">
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="mt-4">
                  <p className="text-3xl font-bold">{stat.value}</p>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Alert Summary */}
      {(severityCounts.critical > 0 || severityCounts.high > 0) && (
        <motion.div
          variants={itemVariants}
          className="rounded-xl border border-destructive/50 bg-destructive/5 p-6"
        >
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-destructive/10">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-destructive">Attention Required</h3>
              <p className="text-sm text-muted-foreground mt-1">
                You have {severityCounts.critical} critical and {severityCounts.high} high
                severity alerts that need immediate attention.
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-3 border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
                asChild
              >
                <Link to="/alerts">View Alerts</Link>
              </Button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Quick Actions */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-xl font-semibold">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className="rounded-xl border bg-card p-6 cursor-pointer transition-shadow hover:shadow-md"
          >
            <Link to="/map" className="block">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue-500/10">
                  <Map className="h-6 w-6 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-semibold">View Map</h3>
                  <p className="text-sm text-muted-foreground">
                    Monitor pipelines and satellite imagery in real-time
                  </p>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.02 }}
            className="rounded-xl border bg-card p-6 cursor-pointer transition-shadow hover:shadow-md"
          >
            <Link to="/analysis" className="block">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple-500/10">
                  <Activity className="h-6 w-6 text-purple-500" />
                </div>
                <div>
                  <h3 className="font-semibold">View Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    Check satellite image analysis results
                  </p>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.02 }}
            className="rounded-xl border bg-card p-6 cursor-pointer transition-shadow hover:shadow-md"
          >
            <Link to="/alerts" className="block">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-orange-500/10">
                  <AlertTriangle className="h-6 w-6 text-orange-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Manage Alerts</h3>
                  <p className="text-sm text-muted-foreground">
                    Review and acknowledge system alerts
                  </p>
                </div>
              </div>
            </Link>
          </motion.div>
        </div>
      </motion.div>

      {/* Recent Activity */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-xl font-semibold">Recent Alerts</h2>
        <div className="rounded-xl border bg-card">
          {alerts.slice(0, 5).length > 0 ? (
            <div className="divide-y">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors"
                >
                  <div
                    className={`p-2 rounded-full ${
                      alert.severity === 'critical'
                        ? 'bg-red-500/10 text-red-500'
                        : alert.severity === 'high'
                          ? 'bg-orange-500/10 text-orange-500'
                          : alert.severity === 'medium'
                            ? 'bg-yellow-500/10 text-yellow-500'
                            : 'bg-blue-500/10 text-blue-500'
                    }`}
                  >
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{alert.title}</p>
                    <p className="text-sm text-muted-foreground truncate">
                      {alert.description}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>{new Date(alert.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No alerts to display</p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

