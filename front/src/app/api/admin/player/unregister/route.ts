import {NextResponse} from "next/server";
import {DefaultApi} from "@/backend_api/backend";
import {EmailSender} from "@/lib/EmailSender";


const senderEmail = process.env.SMTP_USER!;

const emailSender = new EmailSender(
    senderEmail,
    process.env.SMTP_PASS!
);


export async function POST(req: Request) {
  try {
    const { licenceNo }: { licenceNo: string} = await req.json();

    const api = new DefaultApi();
    const response = await api.getAdminPlayerByLicenceNo({licenceNo: licenceNo});
    const player = response.player;

    if (!player) {
      return NextResponse.json({error: 'Player not found.'}, {status: 404});
    }

    const entries = response.entries;

    const entriesNotPaid = entries.filter(entry => !entry.markedAsPaid);

    const updatedEntries = entries.map(entry => {
      return {
        ...entry,
        markedAsPresent: !entry.markedAsPaid ? false : entry.markedAsPresent
      };
    });

    await api.adminRegisterEntries({licenceNo: licenceNo, totalActualPaid: player.totalActualPaid ?? 0, entryInfo: updatedEntries});

    const entryListHTML = entriesNotPaid
        .map((entry) => `<li>Tableau <strong>${entry.categoryId}</strong> : ${entry.alternateName}</li>`)
        .join("");

    const subject = "Tournoi USKB 06/2025 - Annulation de votre inscription";
    const body = `
      <p>Bonjour ${player.firstName},</p>
      
      <p>Nous vous informons que votre inscription au Tournoi National B de l’US Kremlin-Bicêtre, qui se tiendra les 14 et 15 juin 2025, 
      a été annulée en raison de l’absence de paiement anticipé.<?p>

      <p>Conformément à l’article 15 du règlement du tournoi, le paiement anticipé sur notre site internet est obligatoire. 
      Sans règlement dans les délais, l’inscription ne peut être considérée 
      comme valide et nous ne pouvons maintenir votre participation dans les tableaux.</p>

      <p>Malgré plusieurs relances restées sans réponse, nous n’avons pas reçu votre paiement.
      Sauf erreur de notre part, aucun règlement n’a été enregistré.</p>

      <p>Voici un récapitulatif des tableaux pour lesquels votre inscription a été annulée :</p>
      <ul>${entryListHTML}</ul>
      
      <p>Nous espérons avoir le plaisir de vous accueillir lors d’une prochaine édition.</p>
      <p>Sportivement,<br>Le comité d&apos;organisation</p>
      <p>
        <img src="${process.env.NEXT_PUBLIC_SITE_URL}/static/logo.png" alt="Logo USKB" style="margin-top: 8px; width: 120px;" />
      </p>
    `;

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