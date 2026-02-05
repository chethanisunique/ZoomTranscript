import React, { forwardRef, useEffect, useImperativeHandle, useRef } from "react";

export type AudioPlayerProps = {
  src: string;
  onTimeUpdate?: (current: number) => void;
};

export const AudioPlayer = forwardRef<HTMLAudioElement, AudioPlayerProps>(
  ({ src, onTimeUpdate }, ref) => {
    const audioRef = useRef<HTMLAudioElement>(null);

    useImperativeHandle(ref, () => audioRef.current as HTMLAudioElement);

    useEffect(() => {
      const current = audioRef.current;
      if (!current) return;
      const handler = () => onTimeUpdate?.(current.currentTime);
      current.addEventListener("timeupdate", handler);
      return () => current.removeEventListener("timeupdate", handler);
    }, [onTimeUpdate]);

    return <audio ref={audioRef} controls className="w-full my-4" src={src} />;
  },
);

