import {NextResponse} from 'next/server';
import {createCheckoutSession} from "@/lib/payment";

export async function POST(req: Request) {
  try {
    const {licenceNumber, amount, customerEmail} = await req.json();
    const session = await createCheckoutSession(licenceNumber, amount, customerEmail);
    return NextResponse.json({url: session.url});
  } catch (error) {
    console.error(error);
    return NextResponse.json(
        {error: 'An error occurred while creating the checkout session.'},
        {status: 500}
    );
  }
}
