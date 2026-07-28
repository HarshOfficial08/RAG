import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { RequireAuth } from "./auth/RequireAuth";
import { RequireAdmin } from "./auth/RequireAdmin";
import { RedirectIfAuthenticated } from "./auth/RedirectIfAuthenticated";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { SignUp } from "./pages/SignUp";
import { ForgotPassword } from "./pages/ForgotPassword";
import { ResetPassword } from "./pages/ResetPassword";
import { Documents } from "./pages/Documents";
import { AskQuestion } from "./pages/AskQuestion";
import { AuditLog } from "./pages/AuditLog";
import { Settings } from "./pages/Settings";
import { OrgMembers } from "./pages/OrgMembers";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<RedirectIfAuthenticated />}>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
            </Route>
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route element={<RequireAuth />}>
              <Route element={<Layout />}>
                {/* Admin-only routes */}
                <Route element={<RequireAdmin />}>
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/audit-log" element={<AuditLog />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/org/members" element={<OrgMembers />} />
                </Route>
                {/* Shared routes — available to all authenticated users */}
                <Route path="/ask" element={<AskQuestion />} />
                <Route path="/" element={<Navigate to="/ask" replace />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

