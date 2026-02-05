export interface TranscriptSegment {
  speaker: string;
  text: string;
  timestamp: string;
  start: number;
  end: number;
}

export interface Summary {
  overview: string;
  keyPoints: string[];
  participants: string[];
  duration: string;
  actionItems: string[];
}

export interface ProcessAudioResponse {
  transcript: TranscriptSegment[];
  summary: Summary;
  audioUrl: string;
  duration: string;
}
