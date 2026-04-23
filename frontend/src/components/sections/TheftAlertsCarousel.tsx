"use client";

import {
  FinanceCheck, StolenCheck, WriteOffCheck,
  SalvageCheck, ImportStatusCheck,
} from "@/lib/api";
import Card from "@/components/ui/Card";
import SwipeCarousel from "@/components/ui/SwipeCarousel";
import TheftAlertCard from "./TheftAlertCard";
import { DetailRow, icons } from "./shared";

/* Combined Theft & Alerts swipe carousel.
   Used by both FullCheckSection (car) and EVFullCheckSection (EV) so the
   two surfaces stay visually identical. Renders only the checks that have
   data — omits the card entirely when nothing to show. */
export default function TheftAlertsCarousel({
  finance_check,
  stolen_check,
  write_off_check,
  salvage_check,
  import_status,
}: {
  finance_check: FinanceCheck | null;
  stolen_check: StolenCheck | null;
  write_off_check: WriteOffCheck | null;
  salvage_check: SalvageCheck | null;
  import_status: ImportStatusCheck | null;
}) {
  const cards: JSX.Element[] = [];

  if (stolen_check) {
    cards.push(
      <TheftAlertCard
        key="stolen"
        title="Stolen Check"
        description="Checks national police databases to confirm the vehicle has not been reported stolen."
        flagged={stolen_check.stolen}
        flaggedLabel="Reported stolen"
        clearLabel="Not stolen"
        source={stolen_check.data_source}
        details={
          stolen_check.stolen ? (
            <div className="bg-slate-50 rounded-lg p-2 text-sm">
              {stolen_check.reported_date && <DetailRow label="Reported" value={stolen_check.reported_date} />}
              {stolen_check.police_force && <DetailRow label="Police Force" value={stolen_check.police_force} />}
              {stolen_check.reference && <DetailRow label="Reference" value={stolen_check.reference} />}
            </div>
          ) : undefined
        }
      />
    );
  }

  if (finance_check) {
    cards.push(
      <TheftAlertCard
        key="finance"
        title="Finance Check"
        description="Checks whether the vehicle has any outstanding finance agreements registered against it."
        flagged={finance_check.finance_outstanding}
        flaggedLabel={`${finance_check.record_count} active`}
        clearLabel="No finance"
        source={finance_check.data_source}
        details={
          finance_check.finance_outstanding && finance_check.records.length > 0 ? (
            <div className="bg-slate-50 rounded-lg p-2 space-y-2 text-sm">
              {finance_check.records.slice(0, 2).map((r, i) => (
                <div key={i}>
                  <DetailRow label="Agreement" value={r.agreement_type} />
                  <DetailRow label="Lender" value={r.finance_company} />
                  {r.agreement_date && <DetailRow label="Date" value={r.agreement_date} />}
                </div>
              ))}
            </div>
          ) : undefined
        }
      />
    );
  }

  if (write_off_check) {
    const cats = write_off_check.records
      .map((r) => r.category)
      .filter(Boolean)
      .join(" / ");
    cards.push(
      <TheftAlertCard
        key="writeoff"
        title="Write-off Check"
        description="Checks insurance industry records for any history of the vehicle being written off."
        flagged={write_off_check.written_off}
        flaggedLabel={cats ? `Cat ${cats}` : "Written off"}
        clearLabel="Not written off"
        source={write_off_check.data_source}
        details={
          write_off_check.written_off && write_off_check.records.length > 0 ? (
            <div className="bg-slate-50 rounded-lg p-2 text-sm space-y-2">
              {write_off_check.records.slice(0, 2).map((r, i) => (
                <div key={i}>
                  <DetailRow label="Date" value={r.date} />
                  {r.loss_type && <DetailRow label="Loss Type" value={r.loss_type} />}
                  {r.damage_locations && r.damage_locations.length > 0 && (
                    <DetailRow label="Damage" value={r.damage_locations.join(", ")} />
                  )}
                  {r.insurer_name && <DetailRow label="Insurer" value={r.insurer_name} />}
                  {r.claim_number && <DetailRow label="Claim" value={r.claim_number} />}
                </div>
              ))}
            </div>
          ) : undefined
        }
      />
    );
  }

  if (salvage_check) {
    cards.push(
      <TheftAlertCard
        key="salvage"
        title="Salvage Auction Check"
        description="Checks UK salvage auction records for any history of this vehicle being sold as salvage."
        flagged={salvage_check.salvage_found}
        flaggedLabel="Salvage records found"
        clearLabel="No salvage records"
        source={salvage_check.data_source}
      />
    );
  }

  if (import_status) {
    const exported = import_status.is_exported || import_status.marked_for_export;
    const imported = import_status.is_imported;

    // Import card — always shown so buyers know we checked.
    cards.push(
      <TheftAlertCard
        key="import"
        title="Import Status"
        description="An import-registered vehicle may have a different spec, affect warranty, or be harder to insure."
        flagged={imported}
        flaggedLabel="Imported"
        clearLabel="Not imported"
        source={import_status.data_source}
        severity="warn"
      />
    );

    // Export card — DVLA marker = active export process; AutoCheck export = completed.
    cards.push(
      <TheftAlertCard
        key="export"
        title="Export Status"
        description="An export flag means the vehicle has been, or is about to be, permanently shipped outside the UK."
        flagged={exported}
        flaggedLabel={import_status.marked_for_export ? "Marked for export" : "Exported"}
        clearLabel="Not exported"
        source={import_status.data_source}
        severity={import_status.is_exported ? "fail" : "warn"}
      />
    );
  }

  if (cards.length === 0) return null;

  return (
    <Card title="Theft & Alerts" icon={icons.shield} status="neutral">
      <p className="text-xs text-slate-500 mb-3">
        Swipe through each check to see whether the vehicle is flagged.
      </p>
      <SwipeCarousel ariaLabel="Theft and alerts checks" itemNoun="Check">
        {cards}
      </SwipeCarousel>
    </Card>
  );
}
