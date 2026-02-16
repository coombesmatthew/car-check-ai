import { ReactNode } from "react";

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
}

export default function SectionHeader({ title, subtitle, icon }: SectionHeaderProps) {
  return (
    <div className="text-center mb-8">
      {icon && (
        <div className="flex justify-center mb-3">
          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
            {icon}
          </div>
        </div>
      )}
      <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
      {subtitle && (
        <p className="text-slate-500 mt-2 max-w-xl mx-auto">{subtitle}</p>
      )}
    </div>
  );
}
