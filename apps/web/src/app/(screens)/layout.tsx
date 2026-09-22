import { AppHeader } from "@/components/layout/app-header";

export default function ScreensLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="flex-1 p-4">{children}</main>
    </div>
  );
}
