"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";

export function ApiStatus() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => apiClient.health(),
    retry: 1,
  });

  if (isLoading) {
    return (
      <p className="text-sm text-muted" aria-live="polite">
        Підключення до API…
      </p>
    );
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-red-400" aria-live="polite">
        API недоступне
      </p>
    );
  }

  return (
    <p className="text-sm text-muted" aria-live="polite">
      API {data.status} · {data.environment}
    </p>
  );
}
