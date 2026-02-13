import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Car Check AI - Free UK Vehicle Check",
  description:
    "Free MOT history, tax status, mileage clocking detection, ULEZ compliance, and condition scoring for any UK vehicle.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
