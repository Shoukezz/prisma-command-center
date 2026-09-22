import { CommandCenterShell } from "@/features/command-center/components/command-center-shell";

export default function CommandCenterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <CommandCenterShell>{children}</CommandCenterShell>;
}
