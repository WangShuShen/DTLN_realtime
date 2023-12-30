"use client"
import React, { useState, useEffect, useRef } from 'react';

const TestMicrophone: React.FC = () => {
  const [microphoneAccess, setMicrophoneAccess] = useState<string>('Checking...');
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    socketRef.current = new WebSocket("ws://localhost:5000","audio_chunk");

    if (socketRef.current) {
      socketRef.current.onopen = () => console.log('WebSocket connected');
      socketRef.current.onerror = (error: Event) => console.log('WebSocket error:', error);
      socketRef.current.onmessage = (message) => {
        if (audioRef.current) {
          const audioBlob = new Blob([message.data], { 'type' : 'audio/webm; codecs=opus' });
          const audioUrl = URL.createObjectURL(audioBlob);
          audioRef.current.src = audioUrl;
          audioRef.current.play().catch(e => console.error('Error playing audio:', e));
        }
      };
      socketRef.current.onclose = () => console.log('WebSocket disconnected');
    }

    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          setMicrophoneAccess('Microphone access granted');
          mediaRecorderRef.current = new MediaRecorder(stream);
          mediaRecorderRef.current.onstart = () => {
            console.log("MediaRecorder started");
          };
      
          mediaRecorderRef.current.ondataavailable = async (event) => {
            if (event.data.size > 0) {
              // console.log("Data available from MediaRecorder");
              const arrayBuffer = await event.data.arrayBuffer();
              // console.log("Sending audio data:", arrayBuffer)
              if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.send(arrayBuffer);
              }
            } else {
              console.log("No data available from MediaRecorder");
            }
          };
          mediaRecorderRef.current.start(100);
        })
        .catch((err) => {
          setMicrophoneAccess(`Microphone access denied: ${err.message}`);
        });
    } else {
      setMicrophoneAccess('The getUserMedia API is not supported by this browser.');
    }

    return () => {
      socketRef.current?.close();
      mediaRecorderRef.current?.stop();
    };
  }, []);

  return (
    <div>
      <h1>Microphone Test</h1>
      <p>{microphoneAccess}</p>
      <audio ref={audioRef} hidden></audio>
    </div>
  );
};

export default TestMicrophone;



