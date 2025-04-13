import { DefaultApi } from "@/backend_api/backend";
import PlayerFormComponent from "@/app/joueur/[licenceNo]/PlayerFormComponent";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;

  const api = new DefaultApi();


  const ffttPlayer = await api.getPlayer({
    licenceNo: licenceNo,
  });

  if (!ffttPlayer) {
    return <div>Joueur non trouvé</div>;
  }

  const categories = await api.getCategories();

  return (
      <PlayerFormComponent player={ffttPlayer} categories={categories} />
  );
}
