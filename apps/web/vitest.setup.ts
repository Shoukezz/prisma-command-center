import { afterEach, vi } from "vitest";

import "@testing-library/jest-dom/vitest";

// Node's own experimental global `localStorage` (Node 22+) shadows jsdom's and is a
// no-op without `--localstorage-file`, so the app's `window.localStorage` calls would
// silently do nothing. Replace it with a real in-memory implementation.
class MemoryStorage implements Storage {
  private store = new Map<string, string>();

  get length() {
    return this.store.size;
  }

  clear() {
    this.store.clear();
  }

  getItem(key: string) {
    return this.store.get(key) ?? null;
  }

  key(index: number) {
    return Array.from(this.store.keys())[index] ?? null;
  }

  removeItem(key: string) {
    this.store.delete(key);
  }

  setItem(key: string, value: string) {
    this.store.set(key, String(value));
  }
}

vi.stubGlobal("localStorage", new MemoryStorage());

afterEach(() => {
  window.localStorage.clear();
});

class MockWebSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(public url: string) {}

  close() {
    this.onclose?.();
  }

  send() {}
}

// jsdom has no WebSocket implementation; the app opens one on mount for live updates.
vi.stubGlobal("WebSocket", MockWebSocket);
