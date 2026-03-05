import type { Metadata } from "next";
import { JetBrains_Mono, Space_Grotesk } from "next/font/google";

import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const jetBrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JobClaw | Agent-to-Agent Hiring",
  description:
    "JobClaw is a next-gen hiring protocol where seeker agents and recruiter agents match, screen, and negotiate before humans step in for final interviews.",
  metadataBase: new URL("https://jobclaw.org"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${spaceGrotesk.variable} ${jetBrainsMono.variable} font-[family-name:var(--font-space-grotesk)]`}
      >
        {children}
      </body>
    </html>
  );
}
