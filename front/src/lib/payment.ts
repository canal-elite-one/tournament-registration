import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil',
});

export async function createCheckoutSession(licenceNumber: string, amount: number, customerEmail: string) {
  return await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    mode: 'payment',
    line_items: [
      {
        price_data: {
          currency: 'eur', // Change to your currency
          product_data: {
            name: 'Inscription tournoi USKB 06/2025',
          },
          unit_amount: amount * 100, // Amount in cents
        },
        quantity: 1,
      },
    ],
    customer_email: customerEmail,
    success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/joueur/${licenceNumber}/inscription`,
    metadata: {
      licence_number: licenceNumber,
    },
    payment_intent_data: {
      metadata: {
        licence_number: licenceNumber,
      },
    }
  });
}