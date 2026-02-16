interface BadgeProps {
  variant: "pass" | "fail" | "warn" | "neutral" | "info";
  label: string;
  size?: "sm" | "md";
}

const variantStyles = {
  pass: "bg-emerald-100 text-emerald-800 border-emerald-200",
  fail: "bg-red-100 text-red-800 border-red-200",
  warn: "bg-amber-100 text-amber-800 border-amber-200",
  neutral: "bg-slate-100 text-slate-700 border-slate-200",
  info: "bg-blue-100 text-blue-800 border-blue-200",
};

const sizeStyles = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm",
};

export default function Badge({ variant, label, size = "sm" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center font-medium rounded border ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {label}
    </span>
  );
}
