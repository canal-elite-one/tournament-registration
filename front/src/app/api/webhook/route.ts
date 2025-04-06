import {NextResponse} from "next/server";
import Stripe from "stripe";

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
  } catch (err: any) {
    console.error("❌ Webhook signature verification failed.", err.message);
    return NextResponse.json({error: "Invalid signature"}, {status: 400});
  }

  // Handle only successful payments
  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;

    console.log("✅ Payment succeeded!", session);

    try {
      // ✅ Step 3: Call your Python backend here
      // await fetch(process.env.PYTHON_BACKEND_URL!, {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //     "Authorization": `Bearer ${process.env.PYTHON_BACKEND_TOKEN}`, // optional: add security token
      //   },
      //   body: JSON.stringify({
      //     stripeSessionId: session.id,
      //     customerEmail: session.customer_details?.email,
      //     amountTotal: session.amount_total,
      //   }),
      // });
      console.log("✅ Successfully called Python backend!");
    } catch (error) {
      console.error("❌ Failed to call Python backend:", error);
    }
  } else {
    console.log(`Unhandled event type: ${event.type}`);
  }

  return NextResponse.json({received: true});
}
