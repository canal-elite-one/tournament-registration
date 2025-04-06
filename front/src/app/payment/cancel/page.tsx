// app/payment/cancel/page.tsx

"use client";

import {Button, Title, Text, Card} from "@mantine/core";
import {useRouter} from "next/navigation";

export default function PaymentCancelPage() {
  const router = useRouter();

  return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <Card shadow="sm" padding="lg" radius="md" withBorder
              className="w-full max-w-md text-center">
          <Title order={3} className="mb-4">
            Paiement annulé
          </Title>
          <Text className="mb-6">Votre paiement n&#39;a pas été finalisé. Vous pouvez
            réessayer.</Text>
          <Button fullWidth onClick={() => router.push("/payment")}>
            Réessayer
          </Button>
        </Card>
      </div>
  );
}
