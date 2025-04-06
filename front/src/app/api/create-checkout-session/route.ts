// app/api/create-checkout-session/route.ts

import {NextResponse} from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil',
});

export async function POST(req: Request) {
  try {
    const {licenceNumber} = await req.json();
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'payment',
      line_items: [
        {
          price_data: {
            currency: 'eur', // Change to your currency
            product_data: {
              name: 'Inscription tournoi USKB',
            },
            unit_amount: 2000, // Amount in cents (20€)
          },
          quantity: 1,
        },
      ],
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/payment/success`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/payment/cancel`,
      metadata: {
        licence_number: licenceNumber,
      },
    });

    return NextResponse.json({url: session.url});
  } catch (error) {
    console.error(error);
    return NextResponse.json(
        {error: 'An error occurred while creating the checkout session.'},
        {status: 500}
    );
  }
}
