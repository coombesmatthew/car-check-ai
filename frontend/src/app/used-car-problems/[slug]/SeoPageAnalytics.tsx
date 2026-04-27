"use client";

import { useEffect } from "react";
import { track } from "@/lib/analytics";

interface Props {
  slug: string;
  make: string;
  model: string;
  generation: string | null;
}

export default function SeoPageAnalytics({ slug, make, model, generation }: Props) {
  useEffect(() => {
    track("seo_page_viewed", { slug, make, model, generation });
  }, [slug, make, model, generation]);
  return null;
}
