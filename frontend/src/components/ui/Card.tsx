import { ReactNode } from "react";

interface CardProps {
  title: string;
  icon?: ReactNode;
  status?: "pass" | "fail" | "warn" | "neutral";
  children: ReactNode;
}

const borderColors = {
  pass: "border-l-emerald-500",
  fail: "border-l-red-500",
  warn: "border-l-amber-500",
  neutral: "border-l-slate-300",
};

export default function Card({ title, icon, status, children }: CardProps) {
  return (
    <div
      className={`bg-white border border-slate-200 rounded-xl p-5 ${
        status ? `border-l-4 ${borderColors[status]}` : ""
      }`}
    >
      <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
        {icon && <span className="text-slate-400">{icon}</span>}
        {title}
      </h3>
      {children}
    </div>
  );
}
