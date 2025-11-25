import { User } from "lucide-react";
import { cn } from "@/lib/utils";

interface TranscriptSegment {
  speaker: string;
  text: string;
  timestamp: string;
}

interface TranscriptViewProps {
  segments: TranscriptSegment[];
}

export const TranscriptView = ({ segments }: TranscriptViewProps) => {
  return (
    <div className="space-y-6">
      {segments.map((segment, index) => (
        <div
          key={index}
          className="flex gap-4 animate-in fade-in slide-in-from-bottom-4"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="w-5 h-5 text-primary" />
            </div>
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-baseline gap-2">
              <span className="font-semibold text-foreground">{segment.speaker}</span>
              <span className="text-xs text-muted-foreground">{segment.timestamp}</span>
            </div>
            <p className="text-foreground/90 leading-relaxed">{segment.text}</p>
          </div>
        </div>
      ))}
      {segments.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          Upload a recording to see the transcript
        </div>
      )}
    </div>
  );
};
