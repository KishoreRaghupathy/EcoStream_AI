import Link from 'next/link';
import { Wind, BarChart3, MessageSquare } from 'lucide-react';
import { ModeToggle } from '@/components/mode-toggle'; // Assuming I'll add this later or just omit for now

export function Navbar() {
    return (
        <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-16 items-center px-4 container mx-auto">
                <div className="mr-4 hidden md:flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <Wind className="h-6 w-6 text-green-500" />
                        <span className="hidden font-bold sm:inline-block">
                            EcoStream AI
                        </span>
                    </Link>
                    <nav className="flex items-center space-x-6 text-sm font-medium">
                        <Link
                            href="#dashboard"
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            Dashboard
                        </Link>
                        <Link
                            href="#map"
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            Live Map
                        </Link>
                        <Link
                            href="#analyst"
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            AI Analyst
                        </Link>
                    </nav>
                </div>
                <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                    <div className="w-full flex-1 md:w-auto md:flex-none">
                        {/* Search or other controls */}
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="text-xs text-muted-foreground border px-2 py-1 rounded-full bg-muted">
                            Demo Mode
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
