import type { Metadata } from "next";
import SampleReportClient from "./SampleReportClient";

export const metadata: Metadata = {
  title: "Vehicle history report example — see what you get | Vericar",
  description:
    "See exactly what a Vericar vehicle history report includes before you pay. Real sample reports showing finance, write-off, MOT history, valuation and clocking checks.",
  alternates: { canonical: "https://vericar.co.uk/sample-report" },
  openGraph: {
    title: "Vehicle history report example — Vericar",
    description:
      "See exactly what a £9.99 Vericar report includes — finance, write-off, MOT history, valuation, clocking. Real samples.",
    url: "https://vericar.co.uk/sample-report",
    type: "website",
  },
};

export default function SampleReportPage() {
  return <SampleReportClient />;
}
