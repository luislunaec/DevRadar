import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  suffix?: string;
  change?: {
    value: number;
    label: string;
  };
  icon?: ReactNode;
  variant?: 'default' | 'primary' | 'success';
}

export function StatCard({ label, value, suffix, change, icon, variant = 'default' }: StatCardProps) {
  return (
    <div className="glass-card p-6 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className={cn(
          "text-caption uppercase tracking-wider",
          variant === 'primary' && 'text-primary',
          variant === 'success' && 'text-success',
          variant === 'default' && 'text-muted-foreground'
        )}>
          {label}
        </span>
        {icon && (
          <div className={cn(
            "p-2 rounded-lg",
            variant === 'primary' && 'bg-primary/10 text-primary',
            variant === 'success' && 'bg-success/10 text-success',
            variant === 'default' && 'bg-secondary text-muted-foreground'
          )}>
            {icon}
          </div>
        )}
      </div>
      
      <div className="flex items-baseline gap-1">
        <span className="text-h1">{value}</span>
        {suffix && <span className="text-muted-foreground text-lg">{suffix}</span>}
      </div>
      
      {change && (
        <div className="flex items-center gap-1 text-sm">
          <span className={change.value >= 0 ? 'text-success' : 'text-error'}>
            {change.value >= 0 ? '↗' : '↘'}{Math.abs(change.value)}%
          </span>
          <span className="text-muted-foreground">{change.label}</span>
        </div>
      )}
    </div>
  );
}
