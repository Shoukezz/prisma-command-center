import { Panel } from "@/components/ui/panel";

export default function DiplomacyPage() {
  return (
    <Panel title="Дипломатична зала">
      <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center">
        <p className="text-xs font-medium uppercase tracking-wider text-muted">
          Ще не реалізовано
        </p>
        <p className="max-w-sm text-sm text-muted">
          Дипломатичний модуль ще не має бекенду — сторінка навмисно показує цей стан, а не
          порожній екран. Дивіться розділ «Дорожня карта» в README.
        </p>
      </div>
    </Panel>
  );
}
