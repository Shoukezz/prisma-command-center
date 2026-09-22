import type { IntelReport, WorldEvent } from "@/features/command-center/types";

/** Fictional crisis start: 14 MAR 2035 0600Z */
export const CRISIS_START_LABEL = "14 БЕР 2035 0600Z";

export const INITIAL_EVENTS: WorldEvent[] = [
  {
    id: "evt-001",
    gameMinutes: 0,
    title: "SIGINT: Незвичний трафік — Балтійський коридор",
    summary:
      "Поблизу ретранслятора в Гданську виявлено зашифрований пакетний трафік. Патерн не відповідає звичайним логістичним мережам Nordex.",
    severity: "medium",
    region: "Балтійські держави",
    coordinates: { lat: 54.35, lng: 18.65 },
  },
  {
    id: "evt-002",
    gameMinutes: 45,
    title: "Прикордонний інцидент — кордон Східного консорціуму",
    summary:
      "Повідомляють про перестрілку місцевих формувань поблизу Транскаспійського сектору. Союз Aster заперечує причетність; Nordex підвищує готовність.",
    severity: "high",
    region: "Центральна Азія",
    coordinates: { lat: 42.3, lng: 59.6 },
  },
  {
    id: "evt-003",
    gameMinutes: 120,
    title: "Кібервторгнення — вузол партнера PRISMA",
    summary:
      "Спроба горизонтального переміщення у спільній аналітичній VLAN. Загрозу локалізовано; виконавця не встановлено.",
    severity: "critical",
    region: "Західна Європа",
    coordinates: { lat: 50.85, lng: 4.35 },
  },
];

export const INITIAL_INTEL: IntelReport[] = [
  {
    id: "intel-001",
    gameMinutes: 15,
    source: "SATINT",
    confidence: 72,
    title: "Теплова аномалія — порт Чорного моря",
    summary:
      "На допоміжному причалі Одеси посилився тепловий слід. Кількість суден на 2 більша за 48-годинну норму. Тип вантажу не встановлено.",
    region: "Чорне море",
    coordinates: { lat: 46.48, lng: 30.73 },
  },
  {
    id: "intel-002",
    gameMinutes: 90,
    source: "HUMINT",
    confidence: 41,
    title: "Джерело ECHO-7: чутки про мобілізацію консорціуму",
    summary:
      "Ресурс повідомляє про прискорене залізничне переміщення на схід від Тегерана. Не підтверджено; одне джерело.",
    region: "Перська затока",
    coordinates: { lat: 35.7, lng: 51.4 },
  },
  {
    id: "intel-003",
    gameMinutes: 150,
    source: "CYBER",
    confidence: 88,
    title: "Відбиток шкідливого ПЗ — інструментарій SIGINT Aster",
    summary:
      "Відновлений код відповідає каталогу TTP кіберпідрозділу Союзу Aster (ред. 2034-Q4). Імовірно, це стадія розвідки.",
    region: "Північна Атлантика",
    coordinates: { lat: 63.4, lng: -19.0 },
  },
  {
    id: "intel-004",
    gameMinutes: 180,
    source: "SIGINT",
    confidence: 56,
    title: "Командна мережа Nordex — підвищена активність",
    summary:
      "Перехоплення голосових повідомлень у КХ-діапазоні вказують на підвищену готовність 3-ї армійської групи. Переклад частковий.",
    region: "Скандинавія",
    coordinates: { lat: 59.9, lng: 10.75 },
  },
];
