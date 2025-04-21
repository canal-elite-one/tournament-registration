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
    console.log("✅ Payment succeeded!", session);

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
  } else {
    console.log(`Unhandled event type: ${event.type}`);
  }

  return NextResponse.json({received: true});
}
