import { cn } from '@/lib/utils';

interface ProgressBarProps {
  label: string;
  value: number;
  maxValue?: number;
  showPercentage?: boolean;
  variant?: 'primary' | 'gradient';
  size?: 'sm' | 'md';
}

export function ProgressBar({
  label,
  value,
  maxValue = 100,
  showPercentage = true,
  variant = 'primary',
  size = 'md'
}: ProgressBarProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-foreground">{label}</span>
        {showPercentage && (
          <span className="text-sm text-primary font-medium">{Math.round(percentage)}%</span>
        )}
      </div>
      <div className={cn(
        "w-full bg-secondary rounded-full overflow-hidden",
        size === 'sm' ? 'h-1.5' : 'h-2.5'
      )}>
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500 ease-out",
            variant === 'primary' && 'bg-primary',
            variant === 'gradient' && 'bg-gradient-to-r from-primary to-accent-purple'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
