"use client";

import {Card, Text, TextInput, Button} from "@mantine/core";
import {useState} from "react";
import {useRouter} from "next/navigation";
import Image from "next/image";

export default function PlayerSearch() {
  const [licenceNo, setLicenceNumber] = useState<string>("");
  const router = useRouter();

  const handleLicenceSubmit = () => {
    router.push(`/joueur/${licenceNo}`);
  };

  return (
      <Card
          className="max-w-xl mx-auto mt-8 sm:mt-12"
          shadow="md"
          padding="lg"
          radius="lg"
          withBorder
      >
        {/* Logo in top right */}
        <div className="absolute top-4 right-4">
          <Image
              src="/static/logo.png"
              alt="USKB Logo"
              width={40}
              height={40}
              priority
          />
        </div>

        <form onSubmit={handleLicenceSubmit} className="space-y-4">
          <Text size="lg" fw={600} className="mb-4 text-gray-800">
            Inscrivez vous !
          </Text>

          <TextInput
              placeholder="Numéro de licence"
              value={licenceNo}
              onChange={(event) => setLicenceNumber(event.currentTarget.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  handleLicenceSubmit();
                }
              }}
              size="md"
              radius="md"
              required
          />

          <div className="flex justify-end w-full">
            <Button
                type="submit"
                radius="md"
                size="md"
                className="bg-blue-950 hover:bg-blue-700 text-white font-bold"
            >
              Rechercher
            </Button>
          </div>
        </form>
      </Card>
  );
}
