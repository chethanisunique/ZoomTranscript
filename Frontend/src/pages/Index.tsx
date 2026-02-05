import { useState } from "react";
import { FileUpload } from "@/components/FileUpload";
import { TranscriptView } from "@/components/TranscriptView";
import { SummaryView } from "@/components/SummaryView";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Mic2, LoaderCircle } from "lucide-react";
import { toast } from "sonner";
import { ProcessAudioResponse, Summary, TranscriptSegment } from "@/types/api";
import { AudioPlayer } from "@/components/AudioPlayer";

import { useRef } from "react";

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [transcriptData, setTranscriptData] = useState<TranscriptSegment[]>([]);
  const [summaryData, setSummaryData] = useState<Summary | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>("");
  const [activeTab, setActiveTab] = useState("transcript");
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleUpload = async (files: FileList) => {
    if (!files.length) {
      toast.error("No file selected.");
      return;
    }
    const file = files[0];
    setIsLoading(true);
    toast.info("Processing your recording... This may take a moment.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/process-file/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ProcessAudioResponse = await response.json();
      
      if (result.transcript && result.summary && result.audioUrl) {
        setTranscriptData(result.transcript);
        setSummaryData(result.summary);
        setAudioUrl(`http://localhost:8000${result.audioUrl}`);
        toast.success("Processing complete!");
      } else {
        throw new Error("Invalid response from server.");
      }

    } catch (error) {
      console.error("Upload failed:", error);
      toast.error("An error occurred during processing. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const hasResult = transcriptData.length > 0 && summaryData;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Mic2 className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">Transcription Studio</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center gap-4 p-12">
            <LoaderCircle className="w-12 h-12 animate-spin text-primary" />
            <p className="text-muted-foreground">Analyzing audio... Please wait.</p>
          </div>
        ) : !hasResult ? (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-3xl font-bold text-foreground">Upload Your Meeting</h2>
              <p className="text-muted-foreground">
                Upload your Zoom recording to get instant transcription and AI-powered summary
              </p>
            </div>
            <FileUpload onUpload={handleUpload} />
          </div>
        ) : (
          <Card className="border-border bg-card animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <div className="border-b border-border px-6 pt-6">
                <TabsList className="w-full justify-start bg-muted/50">
                  <TabsTrigger value="transcript" className="data-[state=active]:bg-background">
                    Transcript
                  </TabsTrigger>
                  <TabsTrigger value="summary" className="data-[state=active]:bg-background">
                    Summary
                  </TabsTrigger>
                </TabsList>
              </div>
              <div className="p-6">
                <TabsContent value="transcript" className="mt-0 space-y-4">
                  {audioUrl && <AudioPlayer ref={audioRef} src={audioUrl} />}
                  <TranscriptView segments={transcriptData} audioRef={audioRef} />
                </TabsContent>
                <TabsContent value="summary" className="mt-0">
                  {summaryData && <SummaryView summary={summaryData} />}
                </TabsContent>
              </div>
            </Tabs>
          </Card>
        )}
      </main>
    </div>
  );
};

export default Index;
