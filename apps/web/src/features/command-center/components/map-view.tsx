"use client";

import { MapContainer, TileLayer } from "react-leaflet";

import { MapMarkers } from "@/features/command-center/components/map-markers";

const OPEN_STREET_MAP_TILE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";

export function MapView() {
  return (
    <div className="h-full min-h-[360px] w-full [&_.leaflet-container]:h-full [&_.leaflet-container]:min-h-[360px] [&_.leaflet-container]:w-full [&_.leaflet-container]:rounded [&_.leaflet-container]:bg-[#0a0e14]">
      <MapContainer
        center={[35, 25]}
        zoom={3}
        minZoom={2}
        maxZoom={8}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url={OPEN_STREET_MAP_TILE}
        />
        <MapMarkers />
      </MapContainer>
    </div>
  );
}
