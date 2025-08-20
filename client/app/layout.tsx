import type React from "react"
import type { Metadata } from "next"
import { Source_Sans_3 } from "next/font/google"
import "./globals.css"

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-source-sans",
})

export const metadata: Metadata = {
  title: "HirePal - Deloitte Recruiting Assistant",
  description: "AI-powered recruiting assistant for Deloitte",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={sourceSans.variable}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
