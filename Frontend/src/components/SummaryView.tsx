import { FileText, Users, Clock, Target } from "lucide-react";
import { Card } from "@/components/ui/card";

interface SummaryViewProps {
  summary: {
    overview: string;
    keyPoints: string[];
    participants: string[];
    duration: string;
    actionItems: string[];
  } | null;
}

export const SummaryView = ({ summary }: SummaryViewProps) => {
  if (!summary) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Upload a recording to generate a summary
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
      <Card className="p-6 border-border bg-card">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-lg">Overview</h3>
        </div>
        <p className="text-foreground/90 leading-relaxed">{summary.overview}</p>
      </Card>

      <div className="grid md:grid-cols-2 gap-4">
        <Card className="p-6 border-border bg-card">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-primary" />
            <h3 className="font-semibold">Participants</h3>
          </div>
          <ul className="space-y-2">
            {summary.participants.map((participant, index) => (
              <li key={index} className="text-foreground/90">• {participant}</li>
            ))}
          </ul>
        </Card>

        <Card className="p-6 border-border bg-card">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary" />
            <h3 className="font-semibold">Duration</h3>
          </div>
          <p className="text-foreground/90 text-2xl font-bold">{summary.duration}</p>
        </Card>
      </div>

      <Card className="p-6 border-border bg-card">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-lg">Key Points</h3>
        </div>
        <ul className="space-y-3">
          {summary.keyPoints.map((point, index) => (
            <li key={index} className="flex gap-2 text-foreground/90">
              <span className="text-primary font-semibold">{index + 1}.</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </Card>

      {summary.actionItems.length > 0 && (
        <Card className="p-6 border-border bg-card">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-lg">Action Items</h3>
          </div>
          <ul className="space-y-2">
            {summary.actionItems.map((item, index) => (
              <li key={index} className="flex gap-2 text-foreground/90">
                <span className="text-primary">□</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
};
