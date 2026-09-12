import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "StoryForge",
  description: "AI long-form fiction writing system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
