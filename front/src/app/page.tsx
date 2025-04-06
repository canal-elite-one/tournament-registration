'use client';

import {useEffect, useState} from 'react';

export default function HomePage() {
  const [timeLeft, setTimeLeft] = useState<{
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
  }>({days: 0, hours: 0, minutes: 0, seconds: 0});

  useEffect(() => {
    const targetDate = new Date('2025-05-01T10:00:00');

    const updateCountdown = () => {
      const now = new Date();
      const difference = targetDate.getTime() - now.getTime();

      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((difference / (1000 * 60)) % 60);
        const seconds = Math.floor((difference / 1000) % 60);

        setTimeLeft({days, hours, minutes, seconds});
      } else {
        setTimeLeft({days: 0, hours: 0, minutes: 0, seconds: 0});
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
      <main
          className="h-screen bg-contain bg-top bg-no-repeat flex justify-center items-center"
          style={{backgroundImage: "url('/static/countdown-background.jpg')"}}
      >
        <div
            className="
          text-center
          bg-white/30
          backdrop-blur
          rounded-xl
          p-5
        "
        >
          {/* Days */}
          <div className="flex justify-center mb-4">
          <span className="text-[3rem] mx-2 text-[#1836a9]">
            J - {timeLeft.days}
          </span>
          </div>

          {/* Countdown Digits */}
          <div className="flex justify-center space-x-4">
            <span
                className="text-[3rem] text-[#1836a9]">{timeLeft.hours}h</span>
            <span
                className="text-[3rem] text-[#1836a9]">{timeLeft.minutes}m</span>
            <span
                className="text-[3rem] text-[#1836a9]">{timeLeft.seconds}s</span>
          </div>
        </div>
      </main>
  );
}
