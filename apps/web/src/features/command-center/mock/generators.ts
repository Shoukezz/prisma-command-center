import type {
  EventSeverity,
  IntelReport,
  IntelSource,
  MapCoordinates,
  WorldEvent,
} from "@/features/command-center/types";

const REGIONS: { name: string; coordinates: MapCoordinates }[] = [
  { name: "Балтійські держави", coordinates: { lat: 56.9, lng: 24.1 } },
  { name: "Східна Європа", coordinates: { lat: 50.45, lng: 30.52 } },
  { name: "Чорне море", coordinates: { lat: 43.0, lng: 34.0 } },
  { name: "Перська затока", coordinates: { lat: 26.2, lng: 50.6 } },
  { name: "Центральна Азія", coordinates: { lat: 41.3, lng: 69.2 } },
  { name: "Північна Атлантика", coordinates: { lat: 62.0, lng: -15.0 } },
  { name: "Східне Середземномор’я", coordinates: { lat: 35.1, lng: 33.9 } },
  { name: "Південнокитайське море", coordinates: { lat: 12.0, lng: 114.0 } },
];

const EVENT_TEMPLATES: {
  title: string;
  summary: string;
  severity: EventSeverity;
}[] = [
  {
    title: "Повідомлено про прикордонну сутичку",
    summary: "Непідтверджене зіткнення зі стрілецькою зброєю вздовж спірного сектору. Місцеві медіа мовчать.",
    severity: "medium",
  },
  {
    title: "Економічний шок — ринки блоку",
    summary: "Товарні ф’ючерси консорціуму зросли на 8% за дві години. Причина невідома.",
    severity: "low",
  },
  {
    title: "Терористичний інцидент — міська ціль",
    summary: "Вибух саморобного пристрою поблизу урядового кварталу. Дані про жертви попередні.",
    severity: "high",
  },
  {
    title: "Чутки про переворот — регіональна столиця",
    summary: "Дипломатичні повідомлення вказують, що військові оточили парламент. Ситуація швидко змінюється.",
    severity: "critical",
  },
  {
    title: "Кібератака — енергомережа",
    summary: "На двох підстанціях виявлено аномалії SCADA. Активовано резервні системи.",
    severity: "high",
  },
  {
    title: "Переміщення флоту — спірні води",
    summary: "У групи кораблів Nordex зафіксовано прогалини в AIS. Остання позиція — 6 годин тому.",
    severity: "medium",
  },
];

const INTEL_TEMPLATES: {
  source: IntelSource;
  title: string;
  summary: string;
  confidenceRange: [number, number];
}[] = [
  {
    source: "SATINT",
    title: "Знімки — зміна розгортання сил",
    summary: "У передовому районі базування розширено стоянки техніки. Роздільної здатності недостатньо для визначення підрозділу.",
    confidenceRange: [55, 85],
  },
  {
    source: "SIGINT",
    title: "Перехоплення — зашифрований пакет",
    summary: "Короткий пакет у військовому діапазоні. Відкритого тексту не відновлено.",
    confidenceRange: [35, 70],
  },
  {
    source: "HUMINT",
    title: "Польовий звіт — конвой постачання",
    summary: "Джерело стверджує, що нічні конвої перетинають кордон. Надійність не оцінено.",
    confidenceRange: [25, 55],
  },
  {
    source: "CYBER",
    title: "Мережевий маяк — іноземна інфраструктура",
    summary: "Зворотне з’єднання з відомим хостом, пов’язаним з Aster. Можлива операція під чужим прапором.",
    confidenceRange: [45, 92],
  },
];

let idCounter = 1000;

function nextId(prefix: string): string {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

function pick<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)]!;
}

function randomInRange(min: number, max: number): number {
  return Math.floor(min + Math.random() * (max - min + 1));
}

function jitterCoordinates(base: MapCoordinates): MapCoordinates {
  return {
    lat: base.lat + (Math.random() - 0.5) * 4,
    lng: base.lng + (Math.random() - 0.5) * 6,
  };
}

export function generateEvent(gameMinutes: number): WorldEvent {
  const region = pick(REGIONS);
  const template = pick(EVENT_TEMPLATES);
  return {
    id: nextId("evt"),
    gameMinutes,
    title: template.title,
    summary: template.summary,
    severity: template.severity,
    region: region.name,
    coordinates: jitterCoordinates(region.coordinates),
  };
}

export function generateIntelReport(gameMinutes: number): IntelReport {
  const region = pick(REGIONS);
  const template = pick(INTEL_TEMPLATES);
  const [lo, hi] = template.confidenceRange;
  return {
    id: nextId("intel"),
    gameMinutes,
    source: template.source,
    confidence: randomInRange(lo, hi),
    title: template.title,
    summary: template.summary,
    region: region.name,
    coordinates: jitterCoordinates(region.coordinates),
  };
}
