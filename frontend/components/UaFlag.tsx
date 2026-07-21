export function UaFlag({ className = "h-4 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="8" fill="#005BBB" rx="1" />
      <rect y="8" width="24" height="8" fill="#FFD500" rx="1" />
    </svg>
  );
}
