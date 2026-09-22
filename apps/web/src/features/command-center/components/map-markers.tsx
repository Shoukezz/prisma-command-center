"use client";

import { CircleMarker, Popup, useMap } from "react-leaflet";
import { useEffect } from "react";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { formatGameTime } from "@/features/command-center/lib/format-time";

function MapFocusHandler() {
  const map = useMap();
  const selectedEventId = useSimulationStore((s) => s.selectedEventId);
  const selectedIntelId = useSimulationStore((s) => s.selectedIntelId);
  const events = useSimulationStore((s) => s.events);
  const intelReports = useSimulationStore((s) => s.intelReports);

  useEffect(() => {
    const event = events.find((e) => e.id === selectedEventId);
    const intel = intelReports.find((r) => r.id === selectedIntelId);
    const target = event ?? intel;
    if (target) {
      map.flyTo([target.coordinates.lat, target.coordinates.lng], 5, { duration: 0.8 });
    }
  }, [selectedEventId, selectedIntelId, events, intelReports, map]);

  return null;
}

export function MapMarkers() {
  const events = useSimulationStore((s) => s.events);
  const intelReports = useSimulationStore((s) => s.intelReports);
  const selectedEventId = useSimulationStore((s) => s.selectedEventId);
  const selectedIntelId = useSimulationStore((s) => s.selectedIntelId);
  const selectEvent = useSimulationStore((s) => s.selectEvent);
  const selectIntel = useSimulationStore((s) => s.selectIntel);

  return (
    <>
      <MapFocusHandler />
      {events.map((event) => {
        const selected = event.id === selectedEventId;
        return (
          <CircleMarker
            key={event.id}
            center={[event.coordinates.lat, event.coordinates.lng]}
            radius={selected ? 10 : 7}
            pathOptions={{
              color: selected ? "#f97316" : "#ef4444",
              fillColor: selected ? "#f97316" : "#dc2626",
              fillOpacity: 0.85,
              weight: selected ? 3 : 1,
            }}
            eventHandlers={{
              click: () => selectEvent(event.id),
            }}
          >
            <Popup>
              <div className="min-w-[180px] text-xs text-slate-900">
                <p className="font-mono text-[10px] text-slate-600">
                  {formatGameTime(event.gameMinutes)}
                </p>
                <p className="font-semibold">{event.title}</p>
                <p className="mt-1">{event.summary}</p>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
      {intelReports.map((report) => {
        const selected = report.id === selectedIntelId;
        return (
          <CircleMarker
            key={report.id}
            center={[report.coordinates.lat, report.coordinates.lng]}
            radius={selected ? 9 : 6}
            pathOptions={{
              color: selected ? "#38bdf8" : "#3b82f6",
              fillColor: selected ? "#38bdf8" : "#2563eb",
              fillOpacity: 0.75,
              weight: selected ? 3 : 1,
            }}
            eventHandlers={{
              click: () => selectIntel(report.id),
            }}
          >
            <Popup>
              <div className="min-w-[180px] text-xs text-slate-900">
                <p className="font-mono text-[10px] text-slate-600">
                  {report.source} · {report.confidence}%
                </p>
                <p className="font-semibold">{report.title}</p>
                <p className="mt-1">{report.summary}</p>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </>
  );
}
