import Link from "next/link";

const NAV_LINKS = [
  { href: "/command-center", label: "Командний центр" },
  { href: "/intelligence", label: "Розвідка" },
  { href: "/operations", label: "Операції" },
  { href: "/diplomacy", label: "Дипломатія" },
  { href: "/assets", label: "Ресурси" },
  { href: "/analysts", label: "Аналітики" },
] as const;

export function AppHeader() {
  return (
    <header className="flex h-12 shrink-0 items-center gap-6 border-b border-panel-border bg-panel px-4">
      <Link href="/" className="text-sm font-semibold tracking-wide">
        PRISMA
      </Link>
      <nav className="flex flex-1 gap-4 overflow-x-auto text-xs text-muted">
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="whitespace-nowrap hover:text-foreground"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
