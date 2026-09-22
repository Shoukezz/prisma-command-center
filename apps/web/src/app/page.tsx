import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 bg-background p-8">
      <div className="max-w-lg text-center">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-muted">
          Міжнародні стратегічні операції
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">PRISMA</h1>
        <p className="mt-4 text-sm leading-relaxed text-muted">
          2035 рік. Три блоки. Постійна криза. Ви — директор: розвідка, операції та дипломатія
          проходять через цей центр. Ви ніколи не бачите повної картини.
        </p>
      </div>
      <Link
        href="/command-center"
        className="rounded border border-accent/60 bg-accent/10 px-8 py-3 font-mono text-sm uppercase tracking-widest text-accent hover:bg-accent/20"
      >
        Увійти до командного центру
      </Link>
      <p className="font-mono text-[10px] text-slate-600">ПРОТОТИП · ЛОКАЛЬНА СЕСІЯ · ТЕСТОВІ ДАНІ</p>
    </div>
  );
}
