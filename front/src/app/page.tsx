'use client';

import {useEffect, useState} from 'react';
import {TextInput, Button} from '@mantine/core';
import {useRouter} from "next/navigation";

export default function HomePage() {
  const [timeLeft, setTimeLeft] = useState<{
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
  }>({days: 0, hours: 0, minutes: 0, seconds: 0});
  const [licenceNumber, setLicenceNumber] = useState('');
  const [isRegistrationOpen, setIsRegistrationOpen] = useState(false);

  const router = useRouter();

  useEffect(() => {
    const targetDate = new Date('2025-04-01T10:00:00');

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
        setIsRegistrationOpen(true);
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLicenceSubmit = () => {
    router.push(`/joueur/${licenceNumber}`);
  };

  return (
      <main
          className={`h-screen flex justify-center items-center ${
              !isRegistrationOpen ? 'bg-contain bg-top bg-no-repeat' : ''
          }`}
          style={
            !isRegistrationOpen
                ? {backgroundImage: "url('/static/countdown-background.jpg')"}
                : undefined
          }
      >
        {isRegistrationOpen ? (
            <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleLicenceSubmit();
                }}
                className="bg-white/30 backdrop-blur rounded-xl p-5 space-y-4 text-center"
            >
              <TextInput
                  placeholder="Enter your licence number"
                  value={licenceNumber}
                  onChange={(event) => setLicenceNumber(event.currentTarget.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      event.preventDefault();
                      handleLicenceSubmit();
                    }
                  }}
              />
              <Button type="submit" fullWidth>
                Submit
              </Button>
            </form>
        ) : (
            <div className="text-center bg-white/30 backdrop-blur rounded-xl p-5">
              <div className="flex justify-center mb-4">
            <span className="text-[3rem] mx-2 text-[#1836a9]">
              J - {timeLeft.days}
            </span>
              </div>
              <div className="flex justify-center space-x-4">
                <span className="text-[3rem] text-[#1836a9]">{timeLeft.hours}h</span>
                <span className="text-[3rem] text-[#1836a9]">{timeLeft.minutes}m</span>
                <span className="text-[3rem] text-[#1836a9]">{timeLeft.seconds}s</span>
              </div>
            </div>
        )}
      </main>
  );
}
