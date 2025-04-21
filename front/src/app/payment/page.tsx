// app/payment/page.tsx

"use client";

import {Button, Card, Title} from "@mantine/core";
import {notifications} from "@mantine/notifications";

export default function PaymentPage() {
  const handleCheckout = async () => {
    try {
      const response = await fetch("/api/create-checkout-session", {
        method: "POST",
        body: JSON.stringify({
          licenceNumber: "08940975", // Get this from your form state
        }),
      });

      const data = await response.json();

      if (data.url) {
        window.location.href = data.url;
      } else {
        notifications.show({
          title: "Error",
          message: "Could not create checkout session",
          color: "red",
        });
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      notifications.show({
        title: "Error",
        message: error.message,
        color: "red",
      });
    }
  };

  return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <Card shadow="sm" padding="lg" radius="md" withBorder
              className="w-full max-w-md text-center">
          <Title order={3} className="mb-4">
            Paiement de l&#39;inscription
          </Title>
          <Button fullWidth onClick={handleCheckout}>
            Payer avec Stripe
          </Button>
        </Card>
      </div>
  );
}
