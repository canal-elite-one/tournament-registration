import {NextResponse} from "next/server";
import {DefaultApi} from "@/backend_api/backend";
import {EmailSender} from "@/lib/EmailSender";
import {createCheckoutSession} from "@/lib/payment";


const emailSender = new EmailSender(
    process.env.SMTP_USER!,
    process.env.SMTP_PASS!
);

export async function POST(req: Request) {
  try {
    const {licenceNo} = await req.json();

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

    const body = `
      <p>Bonjour ${player.firstName},</p>

      <p>
        Pour finaliser votre inscription au tournoi, un paiement est nécessaire. Cela peut être dû à l’un des cas suivants :
      </p>
      <ul>
        <li>votre précédent paiement a échoué ou n’a pas été validé ;</li>
        <li>vous avez été repêché depuis la liste d’attente et intégré dans le tableau principal.</li>
      </ul>

      <p>
        Afin de confirmer votre participation, veuillez effectuer le règlement via le lien ci-dessous :
      </p>

      <p style="margin: 16px 0;">
        <a href="${session.url}" style="background-color: #2563eb; color: white; padding: 10px 16px; text-decoration: none; border-radius: 6px;">
          Payer mon inscription
        </a>
      </p>

      <p>Voici un récapitulatif des tableaux pour lesquels vous êtes inscrit :</p>
      <ul>${entryListHTML}</ul>

      <p>Montant à régler : <strong>${toPay.toFixed(2)} €</strong></p>

      <p>
        Merci de procéder au paiement dès que possible. Votre inscription ne sera prise en compte qu’après validation du paiement.
      </p>

      <p>Cordialement,<br>L&apos;équipe USKB</p>
    `;

    await emailSender.sendEmail(
        player.email,
        [process.env.ADMIN_EMAIL || ""],
        body,
        "Tournoi USKB 06/2025 - Paiement à valider"
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