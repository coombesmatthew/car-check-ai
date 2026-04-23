/* Turns a buyer-entered asking price + Brego valuation bands into a single
   verdict pill and a clean delta vs mid-market. Five bands:
     bargain  — below trade-in          (emerald, "verify first")
     good     — between trade-in + private sale  (emerald)
     fair     — between private sale + dealer    (blue)
     over     — 0–10% above dealer      (amber)
     bad      — more than 10% above dealer (red)
*/

import type { Valuation } from "./api";

export type PriceVerdictTone = "emerald" | "blue" | "amber" | "red";

export interface PriceVerdict {
  label: string;
  tone: PriceVerdictTone;
  /** Delta vs mid-market (midpoint of private sale + dealer forecourt). £. */
  deltaPounds: number;
  /** Human "£800 above market" / "£120 below market" / "at market price". */
  deltaLabel: string;
  /** One-line explainer shown under the pill. */
  detail: string;
  /** Numeric mid-market reference, for display. */
  midMarketPounds: number;
}

export function computePriceVerdict(
  listingPricePence: number | null | undefined,
  valuation: Valuation | null | undefined,
): PriceVerdict | null {
  if (!listingPricePence || listingPricePence <= 0 || !valuation) return null;
  const priv = valuation.private_sale;
  const dealer = valuation.dealer_forecourt;
  if (priv == null || dealer == null) return null;

  const listingPounds = Math.round(listingPricePence / 100);
  const midMarketPounds = Math.round((priv + dealer) / 2);
  const deltaPounds = listingPounds - midMarketPounds;
  const tradeIn = valuation.trade_in;

  const deltaLabel =
    deltaPounds === 0
      ? "Exactly at market price"
      : deltaPounds < 0
        ? `£${Math.abs(deltaPounds).toLocaleString()} below market`
        : `£${deltaPounds.toLocaleString()} above market`;

  // Below trade-in — suspicious bargain
  if (tradeIn != null && listingPounds < tradeIn) {
    return {
      label: "Bargain",
      tone: "emerald",
      deltaPounds,
      deltaLabel,
      detail:
        "Priced below trade-in — unusually cheap. Great if genuine, but verify the full history carefully first.",
      midMarketPounds,
    };
  }

  // Between trade-in and private sale — good deal
  if (listingPounds <= priv) {
    return {
      label: "Good deal",
      tone: "emerald",
      deltaPounds,
      deltaLabel,
      detail: "Priced at or below a typical private-sale figure.",
      midMarketPounds,
    };
  }

  // Between private sale and dealer forecourt — fair
  if (listingPounds <= dealer) {
    return {
      label: "Fair price",
      tone: "blue",
      deltaPounds,
      deltaLabel,
      detail: "In the normal market range between private sale and dealer forecourt.",
      midMarketPounds,
    };
  }

  // Above dealer forecourt — check how far
  const overPct = ((listingPounds - dealer) / dealer) * 100;
  if (overPct <= 10) {
    return {
      label: "Slightly overpriced",
      tone: "amber",
      deltaPounds,
      deltaLabel,
      detail: "Above the typical dealer asking price — there may be room to negotiate.",
      midMarketPounds,
    };
  }
  return {
    label: "Overpriced",
    tone: "red",
    deltaPounds,
    deltaLabel,
    detail: `£${Math.round(listingPounds - dealer).toLocaleString()} above dealer forecourt asking — worth pushing back hard on price.`,
    midMarketPounds,
  };
}
