import { Badge } from "@/components/ui/badge";

export function StatusBadge({ status }: { status?: string }) {
  const value = status ?? "unknown";
  const tone = value === "succeeded" || value === "ok" ? "green" : value === "failed" ? "red" : value === "partial" ? "amber" : "blue";
  return <Badge tone={tone}>{value}</Badge>;
}

