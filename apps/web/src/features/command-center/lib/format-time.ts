/** Format game minutes as military-style D+NNN HH:MMZ from crisis start. */
export function formatGameTime(gameMinutes: number): string {
  const day = Math.floor(gameMinutes / (24 * 60)) + 1;
  const minutesInDay = gameMinutes % (24 * 60);
  const hours = Math.floor(minutesInDay / 60);
  const minutes = minutesInDay % 60;
  const dayStr = String(day).padStart(3, "0");
  const hourStr = String(hours).padStart(2, "0");
  const minStr = String(minutes).padStart(2, "0");
  return `D+${dayStr} ${hourStr}:${minStr}Z`;
}
