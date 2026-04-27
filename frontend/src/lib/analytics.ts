import posthog from "posthog-js";

export type AnalyticsEvent =
  | "checkout_started"
  | "check_submitted"
  | "report_viewed"
  | "upsell_clicked"
  | "seo_page_viewed"
  | "seo_page_cta_clicked"
  | "seo_sourced_check"
  | "seo_sourced_paid_conversion";

export function track(
  event: AnalyticsEvent,
  properties?: Record<string, unknown>,
): void {
  if (typeof window === "undefined") return;
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return;
  try {
    posthog.capture(event, properties);
  } catch {
    // swallow — analytics must never break the user flow
  }
}

export function identify(
  distinctId: string,
  properties?: Record<string, unknown>,
): void {
  if (typeof window === "undefined") return;
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return;
  try {
    posthog.identify(distinctId, properties);
  } catch {
    // ignore
  }
}
