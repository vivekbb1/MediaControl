import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, RequireAuth } from "@/hooks/useAuth";
import { AppShell } from "@/components/AppShell";
import { HomePage } from "@/pages/HomePage";
import { LoginPage } from "@/pages/LoginPage";
import { RemotePage } from "@/pages/RemotePage";
import { SetupPage } from "@/pages/SetupPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { LocationsPage } from "@/pages/LocationsPage";
import { AddRoomPage } from "@/pages/AddRoomPage";
import { FeaturesPage } from "@/pages/FeaturesPage";

export default function App() {
  return (
    <BrowserRouter basename="/app">
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <RequireAuth>
                <AppShell />
              </RequireAuth>
            }
          >
            <Route index element={<HomePage />} />
            <Route path="features" element={<FeaturesPage />} />
            <Route path="features/:section" element={<FeaturesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="locations" element={<LocationsPage />} />
            <Route path="add" element={<AddRoomPage />} />
            <Route path="d/:location/:room" element={<RemotePage />} />
            <Route path="d/:location/:room/setup" element={<SetupPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
