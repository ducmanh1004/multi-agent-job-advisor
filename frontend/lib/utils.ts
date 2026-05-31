export function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function percent(value: number | undefined) {
  if (typeof value !== "number") return "0%";
  return `${Math.round(value)}%`;
}

