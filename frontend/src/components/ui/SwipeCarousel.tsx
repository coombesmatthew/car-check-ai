"use client";

import { useEffect, useRef, useState, ReactNode, Children } from "react";

interface SwipeCarouselProps {
  children: ReactNode;
  ariaLabel?: string;
  // optional — when provided, shows "Card title 3 of 13" style counter
  itemNoun?: string;
}

export default function SwipeCarousel({
  children,
  ariaLabel = "Swipeable content",
  itemNoun = "Card",
}: SwipeCarouselProps) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const total = Children.count(children);

  const scrollToIndex = (i: number) => {
    const scroller = scrollerRef.current;
    if (!scroller) return;
    const card = scroller.children[i] as HTMLElement | undefined;
    if (card) scroller.scrollTo({ left: card.offsetLeft, behavior: "smooth" });
  };

  useEffect(() => {
    const scroller = scrollerRef.current;
    if (!scroller) return;
    const onScroll = () => {
      const children = Array.from(scroller.children) as HTMLElement[];
      if (!children.length) return;
      // Pick the card whose left edge is closest to the scroll position
      const scrollLeft = scroller.scrollLeft;
      let closest = 0;
      let min = Infinity;
      children.forEach((c, i) => {
        const d = Math.abs(c.offsetLeft - scrollLeft);
        if (d < min) {
          min = d;
          closest = i;
        }
      });
      setActiveIndex(closest);
    };
    scroller.addEventListener("scroll", onScroll, { passive: true });
    return () => scroller.removeEventListener("scroll", onScroll);
  }, []);

  if (total === 0) return null;

  return (
    <div
      role="region"
      aria-roledescription="carousel"
      aria-label={ariaLabel}
      className="relative"
    >
      <div
        ref={scrollerRef}
        className="flex gap-3 overflow-x-auto snap-x snap-mandatory scroll-smooth -mx-1 px-1 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {Children.map(children, (child, i) => (
          <div
            key={i}
            role="group"
            aria-roledescription="slide"
            aria-label={`${itemNoun} ${i + 1} of ${total}`}
            className="snap-start shrink-0 w-[88%] sm:w-[60%] md:w-[48%]"
          >
            {child}
          </div>
        ))}
      </div>

      {total > 1 && (
        <div className="flex items-center justify-between mt-2 px-1">
          <button
            type="button"
            onClick={() => scrollToIndex(Math.max(0, activeIndex - 1))}
            disabled={activeIndex === 0}
            aria-label="Previous"
            className="w-8 h-8 rounded-full border border-slate-200 flex items-center justify-center text-slate-500 disabled:opacity-30 hover:bg-slate-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>

          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              {Array.from({ length: total }).map((_, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => scrollToIndex(i)}
                  aria-label={`Go to ${itemNoun.toLowerCase()} ${i + 1}`}
                  aria-current={i === activeIndex ? "true" : undefined}
                  className={`h-1.5 rounded-full transition-all ${
                    i === activeIndex ? "w-6 bg-slate-700" : "w-1.5 bg-slate-300 hover:bg-slate-400"
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-slate-400 tabular-nums ml-2">
              {activeIndex + 1} of {total}
            </span>
          </div>

          <button
            type="button"
            onClick={() => scrollToIndex(Math.min(total - 1, activeIndex + 1))}
            disabled={activeIndex === total - 1}
            aria-label="Next"
            className="w-8 h-8 rounded-full border border-slate-200 flex items-center justify-center text-slate-500 disabled:opacity-30 hover:bg-slate-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
