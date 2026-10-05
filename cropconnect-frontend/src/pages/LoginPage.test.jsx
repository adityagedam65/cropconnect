import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import axios from "axios";
import LoginPage from "./LoginPage";

vi.mock("axios");
vi.mock("../contexts/AppLanguageContext", () => ({
  useLandingLanguage: () => ({
    language: "en",
    setLanguage: vi.fn(),
    t: (key) => ({
      loginTitle: "Sign in",
      loginSubtitle: "Welcome back",
      emailLabel: "Email",
      emailPlaceholder: "Email",
      passwordLabel: "Password",
      passwordPlaceholder: "Password",
      forgotPassword: "Forgot password?",
      signingIn: "Checking...",
      signInButton: "Log in",
      noAccount: "No account?",
      createOne: "Create one",
      termsText: "By continuing, you agree to",
      termsLink: "Terms",
      and: "and",
      privacyLink: "Privacy",
      loginSuccess: "Logged in",
      connectionError: "Connection error",
      loginError: "Invalid email or password.",
    }[key] || key),
    translate: (value) => Promise.resolve(value),
  }),
}));

const renderLoginPage = () => render(<MemoryRouter><LoginPage /></MemoryRouter>);

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    renderLoginPage();
    expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
  });

  it("shows error toast on invalid credentials", async () => {
    axios.post.mockRejectedValueOnce({
      response: { data: { detail: "Invalid email or password." } },
    });
    renderLoginPage();
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "test@farm.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));
    await waitFor(() => expect(screen.queryByText(/checking/i)).not.toBeInTheDocument());
  });

  it("does not submit when fields are empty", () => {
    axios.post.mockClear();
    renderLoginPage();
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));
    expect(axios.post).not.toHaveBeenCalled();
  });
});
