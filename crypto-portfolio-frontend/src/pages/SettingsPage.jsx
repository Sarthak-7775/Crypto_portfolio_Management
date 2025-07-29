import { SettingsProvider } from "../components/settings/context/SettingsContext";
import UserProfileSettings   from "../components/settings/UserProfileSettings";
import AccountSecuritySettings from "../components/settings/AccountSecuritySettings";
import BankAccountSettings   from "../components/settings/BankAccountSettings";
import LinkedAccountsSettings from "../components/settings/LinkedAccountsSettings";
import ThemeSettings         from "../components/settings/ThemeSettings";
import DocumentUpload        from "../components/settings/DocumentUpload";
import NotificationSettings  from "../components/settings/NotificationSettings";
import PrivacySettings       from "../components/settings/PrivacySettings";

export default function SettingsPage() {
  return (
    <SettingsProvider>
      <main className="p-4 md:p-6 max-w-5xl mx-auto space-y-10">
        <h1 className="text-2xl font-semibold mb-6">Settings</h1>
        <UserProfileSettings />
        <AccountSecuritySettings />
        <BankAccountSettings />
        <LinkedAccountsSettings />
        <ThemeSettings />
        <DocumentUpload />
        <NotificationSettings />
        <PrivacySettings />
      </main>
    </SettingsProvider>
  );
}
