import { CategoryResult, DefaultApi, Player } from "@/backend_api/backend";
import PlayerFormComponent from "@/app/joueur/[licenceNo]/PlayerFormComponent";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;

  const api = new DefaultApi();
  const playerResponse = await api.getPlayer(licenceNo);
  const player = playerResponse.data as Player;

  const categoriesResponse = await api.getCategories();
  const categories = categoriesResponse.data as CategoryResult[];

  if (!player) {
    return <div>Joueur non trouvé</div>;
  }

  return (
      <PlayerFormComponent player={player} categories={categories} />
  );
}
