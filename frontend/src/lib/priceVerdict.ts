/* Turns a buyer-entered asking price + Brego valuation bands into a verdict
   pill + a human-readable reference line. Five bands:
     bargain  — below trade-in          (emerald, "verify first")
     good     — between trade-in + private sale  (emerald)
     fair     — between private sale + dealer    (blue)
     over     — 0–10% above dealer      (amber)
     bad      — more than 10% above dealer (red)
   The reference line anchors the verdict against real Brego figures
   rather than a synthetic midpoint. */

import type { Valuation } from "./api";

export type PriceVerdictTone = "emerald" | "blue" | "amber" | "red";

export interface PriceVerdict {
  label: string;
  tone: PriceVerdictTone;
  /** Short reference sentence anchoring the verdict against a real Brego band. */
  reference: string;
  /** One-line explainer shown under the pill. */
  detail: string;
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
  const tradeIn = valuation.trade_in;
  const fmt = (n: number) => `£${n.toLocaleString()}`;

  // Below trade-in — suspicious bargain
  if (tradeIn != null && listingPounds < tradeIn) {
    return {
      label: "Bargain",
      tone: "emerald",
      reference: `${fmt(tradeIn - listingPounds)} below trade-in value (${fmt(tradeIn)})`,
      detail:
        "Priced below what a dealer would pay as a trade-in. Great if genuine — but verify the full history carefully first.",
    };
  }

  // Between trade-in and private sale — good deal
  if (listingPounds <= priv) {
    return {
      label: "Good deal",
      tone: "emerald",
      reference: `${fmt(priv - listingPounds)} below typical private-sale value (${fmt(priv)})`,
      detail: "Priced at or below what a private seller would typically ask.",
    };
  }

  // Between private sale and dealer forecourt — fair
  if (listingPounds <= dealer) {
    return {
      label: "Fair price",
      tone: "blue",
      reference: `Between private sale (${fmt(priv)}) and dealer forecourt (${fmt(dealer)})`,
      detail: "In the normal market range — private sellers tend to sit at the lower end; dealers at the upper.",
    };
  }

  // Above dealer forecourt — check how far
  const overPct = ((listingPounds - dealer) / dealer) * 100;
  const overDealer = listingPounds - dealer;
  if (overPct <= 10) {
    return {
      label: "Slightly overpriced",
      tone: "amber",
      reference: `${fmt(overDealer)} above dealer forecourt value (${fmt(dealer)})`,
      detail: "Above what even a dealer would typically ask — there may be room to negotiate.",
    };
  }
  return {
    label: "Overpriced",
    tone: "red",
    reference: `${fmt(overDealer)} above dealer forecourt value (${fmt(dealer)})`,
    detail: "Well above dealer forecourt pricing — worth pushing back hard on price before committing.",
  };
}
