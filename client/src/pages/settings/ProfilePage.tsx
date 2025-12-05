import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { User, Building2, Camera, Loader2, Save } from 'lucide-react';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchCurrentUser, updateUser } from '@/store/slices/authSlice';
import { fetchOrganization, updateOrganization } from '@/store/slices/userSlice';
import { authApi } from '@/services/api/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { useToast } from '@/hooks/use-toast';
import { ProfileSkeleton } from '@/components/common/LoadingSkeleton';

const profileSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
});

const organizationSchema = z.object({
  name: z.string().min(2, 'Organization name must be at least 2 characters'),
  description: z.string().optional(),
  website: z.string().url().optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  postal_code: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;
type OrganizationFormData = z.infer<typeof organizationSchema>;

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

export function ProfilePage() {
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { user, isLoading: userLoading } = useAppSelector((state) => state.auth);
  const { organization, isLoading: orgLoading } = useAppSelector((state) => state.user);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    setValue: setProfileValue,
    formState: { errors: profileErrors, isSubmitting: isProfileSubmitting },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  const {
    register: registerOrg,
    handleSubmit: handleOrgSubmit,
    setValue: setOrgValue,
    formState: { errors: orgErrors, isSubmitting: isOrgSubmitting },
  } = useForm<OrganizationFormData>({
    resolver: zodResolver(organizationSchema),
  });

  useEffect(() => {
    dispatch(fetchCurrentUser());
    dispatch(fetchOrganization());
  }, [dispatch]);

  useEffect(() => {
    if (user) {
      setProfileValue('first_name', user.first_name);
      setProfileValue('last_name', user.last_name);
    }
  }, [user, setProfileValue]);

  useEffect(() => {
    if (organization) {
      setOrgValue('name', organization.name);
      setOrgValue('description', organization.description || '');
      setOrgValue('website', organization.website || '');
      setOrgValue('phone', organization.phone || '');
      setOrgValue('address', organization.address || '');
      setOrgValue('city', organization.city || '');
      setOrgValue('state', organization.state || '');
      setOrgValue('country', organization.country || '');
      setOrgValue('postal_code', organization.postal_code || '');
    }
  }, [organization, setOrgValue]);

  const handleAvatarChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploadingAvatar(true);
    try {
      const updatedUser = await authApi.updateAvatar(file);
      dispatch(updateUser(updatedUser));
      toast({
        title: 'Avatar updated',
        description: 'Your profile picture has been updated.',
        variant: 'success',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update avatar. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const onProfileSubmit = async (data: ProfileFormData) => {
    try {
      const updatedUser = await authApi.updateProfile(data);
      dispatch(updateUser(updatedUser));
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
        variant: 'success',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update profile. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const onOrganizationSubmit = async (data: OrganizationFormData) => {
    const result = await dispatch(updateOrganization(data));
    if (updateOrganization.fulfilled.match(result)) {
      toast({
        title: 'Organization updated',
        description: 'Your organization details have been updated.',
        variant: 'success',
      });
    } else {
      toast({
        title: 'Error',
        description: 'Failed to update organization. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const getInitials = () => {
    if (!user) return 'U';
    const first = user.first_name?.[0] || '';
    const last = user.last_name?.[0] || '';
    return (first + last).toUpperCase() || user.email[0].toUpperCase();
  };

  if ((userLoading || orgLoading) && !user) {
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
        <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground">Manage your personal information</p>
      </motion.div>

      {/* Avatar Section */}
      <motion.section variants={itemVariants} className="mb-8">
        <div className="flex items-center gap-6">
          <div className="relative">
            <Avatar className="h-24 w-24">
              {user?.avatar && <AvatarImage src={user.avatar} alt={user.full_name} />}
              <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                {getInitials()}
              </AvatarFallback>
            </Avatar>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploadingAvatar}
              className="absolute bottom-0 right-0 p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              {isUploadingAvatar ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Camera className="h-4 w-4" />
              )}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              className="hidden"
            />
          </div>
          <div>
            <h2 className="text-xl font-semibold">{user?.full_name || 'User'}</h2>
            <p className="text-muted-foreground">{user?.email}</p>
          </div>
        </div>
      </motion.section>

      {/* Personal Information */}
      <motion.section variants={itemVariants} className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <User className="h-5 w-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Personal Information</h2>
        </div>
        <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="rounded-lg border p-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                {...registerProfile('first_name')}
                className={profileErrors.first_name ? 'border-destructive' : ''}
              />
              {profileErrors.first_name && (
                <p className="text-sm text-destructive">{profileErrors.first_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                {...registerProfile('last_name')}
                className={profileErrors.last_name ? 'border-destructive' : ''}
              />
              {profileErrors.last_name && (
                <p className="text-sm text-destructive">{profileErrors.last_name.message}</p>
              )}
            </div>
          </div>
          <Button type="submit" disabled={isProfileSubmitting}>
            {isProfileSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Profile
              </>
            )}
          </Button>
        </form>
      </motion.section>

      {/* Organization */}
      <motion.section variants={itemVariants}>
        <div className="flex items-center gap-2 mb-4">
          <Building2 className="h-5 w-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Organization</h2>
        </div>
        <form onSubmit={handleOrgSubmit(onOrganizationSubmit)} className="rounded-lg border p-4">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="org_name">Organization Name</Label>
                <Input
                  id="org_name"
                  {...registerOrg('name')}
                  className={orgErrors.name ? 'border-destructive' : ''}
                />
                {orgErrors.name && (
                  <p className="text-sm text-destructive">{orgErrors.name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="website">Website</Label>
                <Input
                  id="website"
                  type="url"
                  placeholder="https://example.com"
                  {...registerOrg('website')}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                {...registerOrg('description')}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" {...registerOrg('phone')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="address">Address</Label>
                <Input id="address" {...registerOrg('address')} />
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="city">City</Label>
                <Input id="city" {...registerOrg('city')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Input id="state" {...registerOrg('state')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="country">Country</Label>
                <Input id="country" {...registerOrg('country')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="postal_code">Postal Code</Label>
                <Input id="postal_code" {...registerOrg('postal_code')} />
              </div>
            </div>
          </div>
          <Button type="submit" className="mt-4" disabled={isOrgSubmitting}>
            {isOrgSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Organization
              </>
            )}
          </Button>
        </form>
      </motion.section>
    </motion.div>
  );
}

