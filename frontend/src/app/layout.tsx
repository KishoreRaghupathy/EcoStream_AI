import type { Metadata } from "next";
import { Inter } from "next/font/google"; // Using Inter as requested/preferred
import "./globals.css";
import Providers from "@/components/providers";
import { Navbar } from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EcoStream AI - Intelligent Air Quality Monitoring",
  description: "Real-time air quality forecasting and AI analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background flex flex-col">
            <Navbar />
            <main className="flex-1">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
