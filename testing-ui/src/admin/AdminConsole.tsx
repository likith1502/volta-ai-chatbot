import React from 'react';
import { OriginalApp } from '../App';

/**
 * AdminConsole — wraps the existing App (the developer/admin console)
 * and mounts it under the /admin route.
 *
 * This component simply delegates to the original App, keeping all existing
 * admin functionality intact. No admin features have been modified.
 */
export const AdminConsole: React.FC = () => {
  return <OriginalApp />;
};

export default AdminConsole;
