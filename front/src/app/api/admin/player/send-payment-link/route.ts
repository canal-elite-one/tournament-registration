import {NextResponse} from "next/server";
import {DefaultApi} from "@/backend_api/backend";
import {EmailSender} from "@/lib/EmailSender";
import {createCheckoutSession} from "@/lib/payment";


const senderEmail = process.env.SMTP_USER!;

const emailSender = new EmailSender(
    senderEmail,
    process.env.SMTP_PASS!
);

type TemplateType = "payment-link" | "last-warning";


export async function POST(req: Request) {
  try {
    const { licenceNo, template, deadline }: { licenceNo: string; template: TemplateType; deadline?: string } = await req.json();

    const api = new DefaultApi();
    const response = await api.getAdminPlayerByLicenceNo({licenceNo: licenceNo});
    const player = response.player;

    if (!player) {
      return NextResponse.json({error: 'Player not found.'}, {status: 404});
    }

    const entries = response.entries;

    const entriesNotPaidMain = entries.filter(entry => !entry.markedAsPaid && entry.rank <= Math.floor(entry.maxPlayers * (1 + entry.overbookingPercentage/100.0)));
    const toPay = entriesNotPaidMain.reduce((acc, entry) => acc + entry.baseRegistrationFee, 0);

    if (toPay === 0) {
      return NextResponse.json({message: 'No payment required.'}, {status: 200});
    }

    const session = await createCheckoutSession(licenceNo, toPay, player.email);

    const entryListHTML = entriesNotPaidMain
        .map((entry) => `<li>Tableau <strong>${entry.categoryId}</strong> : ${entry.alternateName}</li>`)
        .join("");

    const registrationSummary = `
    <p>Voici un récapitulatif des tableaux pour lesquels vous êtes inscrit :</p>
    <ul>${entryListHTML}</ul>
    
    <p>Montant à régler : <strong>${toPay.toFixed(2)} €</strong></p>
    `;

    const paymentLink = `
      <p>
        Afin de confirmer votre participation, veuillez effectuer le règlement via le lien ci-dessous :
      </p>
    
      <p style="margin: 16px 0;">
        <a href="${session.url}" style="background-color: #2563eb; color: white; padding: 10px 16px; text-decoration: none; border-radius: 6px;">
          Payer mon inscription
        </a>
      </p>
    `;

    const signature = `
      <p>
        Merci de procéder au paiement dès que possible. Votre inscription ne sera prise en compte qu’après validation du paiement.
      </p>
      <p>Sportivement,<br>L&apos;équipe USKB</p>
      <p>
        <img src="${process.env.NEXT_PUBLIC_SITE_URL}/static/logo.png" alt="Logo USKB" style="margin-top: 8px; width: 120px;" />
      </p>`;

    const expirationLinkInfo = `
      <p style="background-color: #dbeafe; color: #1e40af; padding: 12px; border-radius: 6px; border: 1px solid #93c5fd; font-size: 14px;">
        ℹ️ <strong>Note :</strong> Le lien de paiement expirera automatiquement <strong>24h après la réception de cet e-mail</strong>.<br>
        Si vous ne parvenez pas à effectuer le paiement à temps, merci de nous contacter à l'adresse suivante : <a href="${senderEmail}" style="color: #1e40af;"><strong>${senderEmail}</strong></a> afin de recevoir un nouveau lien.
      </p>
    `;


    let subject = "";
    let body = "";

    if (template === "payment-link") {
      subject = "Tournoi USKB 06/2025 - Paiement à valider";
      body = `
      <p>Bonjour ${player.firstName},</p>
    
      <p>
        Pour finaliser votre inscription au tournoi, un paiement est nécessaire. Cela peut être dû à l’un des cas suivants :
      </p>
      <ul>
        <li>votre précédent paiement a échoué ou n’a pas été validé ;</li>
        <li>vous avez été repêché depuis la liste d’attente et intégré dans le tableau principal ;</li>
        <li>vous nous avez demander de vous envoyer un nouveau lien.</li>
      </ul>
    
      ${paymentLink}
    
      ${registrationSummary}
      
      ${expirationLinkInfo}
      ${signature}`;
    } else if (template === "last-warning") {
      if (!deadline) {
        return NextResponse.json({error: 'Deadline is required for last warning template.'}, {status: 400});
      }

      const deadlineDate = new Date(deadline).toLocaleString("fr-FR", {
        dateStyle: "full",
        timeStyle: "short",
      });

      subject = "[URGENT] Tournoi USKB 06/2025 - Dernier rappel pour paiement";
      body = `
        <p>Bonjour ${player.firstName},</p>

        <p>Ceci est un <strong>dernier rappel</strong> pour procéder au paiement de votre inscription.</p>

        ${paymentLink}
    
        ${registrationSummary}
        
        <p style="background-color: #f8d7da; color: #721c24; padding: 12px; border-radius: 6px; border: 1px solid #f5c6cb;">
          ⚠️ <strong>Vous avez jusqu'au ${deadlineDate} pour effectuer le règlement de votre inscription.</strong> Passé ce délai, les places seront réattribuées aux personnes sur liste d’attente.
        </p>
      
        ${expirationLinkInfo}
        ${signature}`;
    } else {
      return NextResponse.json({error: 'Invalid template type.'}, {status: 400});
    }

    await emailSender.sendEmail(
        player.email,
        [process.env.ADMIN_EMAIL!],
        body,
        subject
    );

    return NextResponse.json({ message: "Email sent." }, { status: 200 });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    console.error(await error.response.json());
    return NextResponse.json(
        {error: 'An error occurred on player payment.'},
        {status: 500}
    );
  }
}