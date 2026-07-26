import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const origin = `${protocol}://${host}`;
  const title = "TJU Quiz Hub｜天大刷题站";
  const description = "天津大学学生的轻量刷题站：章节检测、综合训练、模拟考试、错题回顾与成绩追踪。";
  const image = new URL("/og.png", origin).toString();

  return {
    metadataBase: new URL(origin),
    title: { default: title, template: "%s｜TJU Quiz Hub" },
    description,
    openGraph: {
      title,
      description,
      type: "website",
      images: [{ url: image, width: 1731, height: 909, alt: "TJU Quiz Hub 天大刷题站" }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
