import {NextResponse} from "next/server";
import Stripe from "stripe";
import {DefaultApi} from "@/backend_api/backend";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-03-31.basil",
});

// Important: Stripe needs the raw body for signature verification
export async function POST(req: Request) {
  const signature = req.headers.get("stripe-signature") as string;
  const body = await req.text();

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
        body,
        signature,
        process.env.STRIPE_WEBHOOK_SECRET!
    );
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (err: any) {
    console.error("❌ Webhook signature verification failed.", err.message);
    return NextResponse.json({error: "Invalid signature"}, {status: 400});
  }

  // Handle only successful payments
  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;

    const sessionData = {
      id: session.id,
      metadata: session.metadata || {},
      amount_total: session.amount_total,
    }

    console.log("✅ Payment succeeded!", sessionData);

    const licenceNo = session.metadata?.licence_number;

    if(!licenceNo) {
      console.error("❌ Licence number not found in session metadata");
      return NextResponse.json({error: "Licence number not found"}, {status: 400});
    }

    const api = new DefaultApi();

    try {
      await api.pay({licenceNo: licenceNo, payBody: {amount: (session.amount_total || 0) / 100}});
      console.log("✅ Successfully called Python backend!");
    } catch (error) {
      console.error("❌ Failed to call Python backend:", error);
    }
  } else if (event.type === "checkout.session.expired") {
    const session = event.data.object as Stripe.Checkout.Session;

    const sessionData = {
      id: session.id,
      metadata: session.metadata || {},
      amount_total: session.amount_total,
    }

    console.log("⚠️ Payment session expired!", sessionData);
  }
   else if (event.type === "payment_intent.payment_failed") {
     // TODO: if we have time, send this to backend to receive an email
    const paymentIntent = event.data.object;

    const failureMessage = paymentIntent.last_payment_error?.message;
    const failureCode = paymentIntent.last_payment_error?.code;

    console.log(`Payment failed for customer ${paymentIntent.metadata?.licence_number}`);
    console.log(`Failure code: ${failureCode}`);
    console.log(`Failure message: ${failureMessage}`);
    console.log(`Amount: ${paymentIntent.amount}`);
    console.log("❌ Payment failed!", event.data.object);
  }
  else {
    console.log(`Unhandled event type: ${event.type}`);
  }

  return NextResponse.json({received: true});
}
