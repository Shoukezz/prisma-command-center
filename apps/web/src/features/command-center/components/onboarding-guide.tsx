"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "prisma-onboarding-complete";

type GuideTarget = "events" | "map" | "intelligence" | "operations" | "time" | null;
type Requirement = "event" | "intel" | "operation" | "time";

interface MissionStep {
  target: GuideTarget;
  eyebrow: string;
  title: string;
  body: string;
  requirement?: Requirement;
  hint?: string;
}

const STEPS: readonly MissionStep[] = [
  {
    target: null,
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 01",
    title: "Операція «Тиха хвиля»",
    body: "Директоре, у кількох регіонах зростає напруженість. Штаб отримав суперечливі сигнали, а політичне керівництво чекає на вашу оцінку. Це не тест: кожна ваша дія впливає на світ.",
  },
  {
    target: "events",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 02",
    title: "Зафіксуйте оперативний сигнал",
    body: "Почніть зі стрічки подій ліворуч. Оберіть будь-яке зведення: так ви позначите район інтересу на мапі. Спочатку ми бачимо подію, а не її повну причину.",
    requirement: "event",
    hint: "Оберіть одну подію у лівій стрічці, щоб продовжити.",
  },
  {
    target: "map",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 03",
    title: "Оцініть контекст на мапі",
    body: "Червоні мітки — підтверджені події, сині — розвіддані. Натискайте мітки, щоб зіставити їхній час, місце та опис. Близькість сигналів не завжди означає причинний зв’язок.",
  },
  {
    target: "intelligence",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 04",
    title: "Відкрийте розвідувальний звіт",
    body: "Тепер оберіть будь-який звіт у правій стрічці. Відсоток поруч із ним — це заявлена достовірність джерела, а не гарантія правди. Ваша задача — зважити ризик помилки.",
    requirement: "intel",
    hint: "Оберіть розвідувальний звіт праворуч, щоб продовжити.",
  },
  {
    target: "intelligence",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 05",
    title: "Послухайте аналітиків",
    body: "Розгорнутий звіт містить незалежні оцінки аналітиків. Вони можуть не погоджуватися з джерелом і між собою — це навмисно. Порівнюйте спеціалізацію, упередження та їхню власну оцінку ймовірності.",
  },
  {
    target: "intelligence",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 06",
    title: "Не плутайте впевненість із доказом",
    body: "Якщо даних недостатньо, натисніть «Запитати розвіддані» у відкритому звіті. Так ви отримаєте уточнений збір даних, але криза продовжує розвиватися. Після дії за потреби оберіть звіт знову.",
  },
  {
    target: "operations",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 07",
    title: "Санкціонуйте обережну операцію",
    body: "Оберіть розвідувальний звіт, а потім натисніть «Спланувати розвідку» внизу екрана. Розвідка — безпечніший перший крок, ніж удар: вона витрачає ресурс, але може зменшити невизначеність.",
    requirement: "operation",
    hint: "Сплануйте одну розвідувальну операцію, щоб продовжити.",
  },
  {
    target: "operations",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 08",
    title: "Контролюйте ціну рішення",
    body: "У черзі операцій видно ресурс, ціль, статус і час завершення. Успіх залежить не лише від заявленої достовірності, а й від прихованої точності самих даних. Результат може змінити ситуацію в регіоні.",
  },
  {
    target: "time",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 09",
    title: "Дайте операції завершитися",
    body: "Натисніть «+1 година» або продовжте час. Це завершить навчальну розвідку та покаже її результат у черзі. Пауза корисна для аналізу, але світ не чекатиме вічно.",
    requirement: "time",
    hint: "Просуньте ігровий час щонайменше на одну годину.",
  },
  {
    target: "operations",
    eyebrow: "НАВЧАЛЬНА МІСІЯ · 10",
    title: "Підбийте підсумок",
    body: "Перегляньте результат операції внизу екрана. Тепер ви знаєте основний цикл PRISMA: подія → розвідка → аналіз → рішення → наслідки. Наступні кризи не матимуть правильних відповідей — лише обґрунтовані рішення.",
  },
  {
    target: null,
    eyebrow: "НАВЧАЛЬНА МІСІЯ · ЗАВЕРШЕНО",
    title: "Командування у ваших руках",
    body: "Ви завершили операцію «Тиха хвиля». Використовуйте кнопку «НАВЧАННЯ» у верхній панелі, якщо захочете пройти місію ще раз.",
  },
];

interface OnboardingGuideProps {
  onTargetChange: (target: GuideTarget) => void;
  selectedEventId: string | null;
  selectedIntelId: string | null;
  operationsCount: number;
  gameMinutes: number;
  isHydrated: boolean;
}

export function OnboardingGuide({
  onTargetChange,
  selectedEventId,
  selectedIntelId,
  operationsCount,
  gameMinutes,
  isHydrated,
}: OnboardingGuideProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [missionStart, setMissionStart] = useState({ operationsCount: 0, gameMinutes: 0 });
  const [hasCheckedStorage, setHasCheckedStorage] = useState(false);

  if (isHydrated && !hasCheckedStorage) {
    setHasCheckedStorage(true);
    if (window.localStorage.getItem(STORAGE_KEY) !== "true") {
      setMissionStart({ operationsCount, gameMinutes });
      setIsOpen(true);
    }
  }

  useEffect(() => {
    onTargetChange(isOpen ? STEPS[stepIndex].target : null);
  }, [isOpen, onTargetChange, stepIndex]);

  const openMission = () => {
    setMissionStart({ operationsCount, gameMinutes });
    setStepIndex(0);
    setIsOpen(true);
  };

  const close = (completed: boolean) => {
    if (completed) window.localStorage.setItem(STORAGE_KEY, "true");
    setIsOpen(false);
  };

  const requirementMet = (requirement: Requirement | undefined) => {
    if (!requirement) return true;
    if (requirement === "event") return selectedEventId !== null;
    if (requirement === "intel") return selectedIntelId !== null;
    if (requirement === "operation") return operationsCount > missionStart.operationsCount;
    return gameMinutes >= missionStart.gameMinutes + 60;
  };

  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;
  const isReady = requirementMet(step.requirement);

  return (
    <>
      <button
        type="button"
        onClick={openMission}
        className="rounded border border-panel-border px-2 py-1 text-[10px] text-muted transition-colors hover:border-accent hover:text-foreground"
      >
        НАВЧАННЯ
      </button>

      {isOpen ? (
        <div className="pointer-events-none fixed inset-x-0 bottom-0 z-50 p-3 sm:bottom-4 sm:left-4 sm:right-auto sm:w-[420px]">
          <section className="pointer-events-auto border border-accent/60 bg-panel/95 p-4 shadow-2xl backdrop-blur">
            <div className="mb-3 flex items-center justify-between gap-4">
              <p className="font-mono text-[10px] tracking-[0.16em] text-accent">{step.eyebrow}</p>
              <span className="font-mono text-[10px] text-muted">{stepIndex + 1}/{STEPS.length}</span>
            </div>
            <h2 className="text-base font-semibold text-foreground">{step.title}</h2>
            <p className="mt-2 text-xs leading-relaxed text-muted">{step.body}</p>
            {step.hint && !isReady ? (
              <p className="mt-3 border-l-2 border-amber-400 pl-2 text-[11px] text-amber-200">{step.hint}</p>
            ) : null}
            <div className="mt-4 flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => close(false)}
                className="px-2 py-1.5 text-xs text-muted hover:text-foreground"
              >
                Вийти з місії
              </button>
              <div className="flex gap-2">
                {stepIndex > 0 ? (
                  <button
                    type="button"
                    onClick={() => setStepIndex((index) => index - 1)}
                    className="rounded border border-panel-border px-3 py-1.5 text-xs text-muted hover:text-foreground"
                  >
                    Назад
                  </button>
                ) : null}
                <button
                  type="button"
                  disabled={!isReady}
                  onClick={() => (isLast ? close(true) : setStepIndex((index) => index + 1))}
                  className="rounded bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent/80 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isLast ? "Завершити місію" : "Продовжити"}
                </button>
              </div>
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}
