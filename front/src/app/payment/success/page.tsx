// app/payment/success/page.tsx

"use client";

import {Button, Title, Text, Card} from "@mantine/core";
import {useRouter} from "next/navigation";

export default function PaymentSuccessPage() {
  const router = useRouter();

  return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <Card shadow="sm" padding="lg" radius="md" withBorder
              className="w-full max-w-md text-center">
          <Title order={3} className="mb-4">
            Paiement réussi 🎉
          </Title>
          <Text className="mb-6">Merci pour votre inscription au tournoi USKB !</Text>
          <Button fullWidth onClick={() => router.push("/")}>
            Retour à l&#39;accueil
          </Button>
        </Card>
      </div>
  );
}
