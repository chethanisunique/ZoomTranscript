import { Upload } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onUpload: (files: FileList) => void;
}

export const FileUpload = ({ onUpload }: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files?.length > 0) {
      onUpload(files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files?.length > 0) {
      onUpload(files);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "relative border-2 border-dashed rounded-xl p-12 transition-all duration-300 hover:border-primary/50",
        isDragging ? "border-primary bg-primary/5 scale-[1.02]" : "border-border bg-card"
      )}
    >
      <input
        type="file"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        multiple
        accept=".zip,.mp3,.mp4,.m4a,.wav"
      />
      <div className="flex flex-col items-center gap-4 pointer-events-none">
        <div className={cn(
          "p-4 rounded-full transition-all duration-300",
          isDragging ? "bg-primary/20 scale-110" : "bg-muted"
        )}>
          <Upload className={cn(
            "w-8 h-8 transition-colors duration-300",
            isDragging ? "text-primary" : "text-muted-foreground"
          )} />
        </div>
        <div className="text-center">
          <p className="text-lg font-medium text-foreground mb-1">
            Drop your Zoom recording here
          </p>
          <p className="text-sm text-muted-foreground">
            or click to browse files
          </p>
        </div>
      </div>
    </div>
  );
};
