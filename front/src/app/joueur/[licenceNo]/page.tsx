import {DefaultApi} from "@/backend_api/backend";
import PlayerFormComponent from "@/app/joueur/[licenceNo]/PlayerFormComponent";
import {redirect} from "next/navigation";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;

  const api = new DefaultApi();

  try {
    const ffttPlayer = await api.getPlayer({
      licenceNo: licenceNo,
    });

    const categories = await api.getCategories();

    return (
        <PlayerFormComponent player={ffttPlayer} categories={categories} />
    );
  } catch (error: any) {
    const statusCode = error.response?.status;

    if (statusCode === 403) {
      redirect(`/joueur/${licenceNo}/inscription`);
    }

    if (statusCode === 404) {
      return <div>Le joueur avec le numéro de licence ${licenceNo} n&apos;a pas été trouvé</div>
    }

    if (statusCode === 500) {
      // TODO: unexpected error, try again later
    }
    redirect("/");
  }
}
