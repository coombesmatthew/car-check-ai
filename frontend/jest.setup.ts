import "@testing-library/jest-dom";

// Mock next/navigation — the App Router hooks throw an invariant outside a
// real router context, so jsdom-based tests need a stub.
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    refresh: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
  useParams: () => ({}),
  redirect: jest.fn(),
  notFound: jest.fn(),
}));

// jsdom doesn't implement IntersectionObserver — used by hooks like
// useActiveSection. A no-op stub is enough for component tests.
class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | Document | null = null;
  readonly rootMargin: string = "";
  readonly thresholds: ReadonlyArray<number> = [];
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
  takeRecords = jest.fn(() => [] as IntersectionObserverEntry[]);
}
global.IntersectionObserver =
  MockIntersectionObserver as unknown as typeof IntersectionObserver;

// jsdom doesn't ship `fetch`. Provide a default jest mock so components that
// fire fetches in useEffect (e.g. KnownIssuesCard) don't blow up. Individual
// tests can override per-call via `(global.fetch as jest.Mock).mockResolvedValue(...)`.
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(""),
  } as Response),
) as jest.Mock;

// jsdom doesn't implement Element.scrollIntoView — used by SwipeCarousel etc.
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = jest.fn();
}
