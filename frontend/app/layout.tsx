import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "EquateAI — Scientific Equation Platform",
  description:
    "AI-powered scientific document and equation parsing, reasoning & knowledge discovery",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased font-sans">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
