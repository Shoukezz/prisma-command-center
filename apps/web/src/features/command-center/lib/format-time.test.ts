import { describe, expect, it } from "vitest";

import { formatGameTime } from "./format-time";

describe("formatGameTime", () => {
  it("formats the start of the crisis as day 1, midnight", () => {
    expect(formatGameTime(0)).toBe("D+001 00:00Z");
  });

  it("pads hours and minutes to two digits", () => {
    expect(formatGameTime(65)).toBe("D+001 01:05Z");
  });

  it("rolls over into a new day after 24 hours", () => {
    expect(formatGameTime(24 * 60)).toBe("D+002 00:00Z");
  });

  it("pads the day counter to three digits for a long crisis", () => {
    expect(formatGameTime(41 * 24 * 60)).toBe("D+042 00:00Z");
  });

  it("handles a time within the last minute of a day", () => {
    expect(formatGameTime(24 * 60 - 1)).toBe("D+001 23:59Z");
  });
});
