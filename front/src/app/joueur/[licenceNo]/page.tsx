import { Category, DefaultApi, Player } from "@/backend_api/backend";
import PlayerFormComponent from "@/app/joueur/[licenceNo]/PlayerFormComponent";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;

  const api = new DefaultApi();
  const playerResponse = await api.apiPublicGetPlayerPlayersLicenceNoGet(licenceNo);
  const player = playerResponse.data as Player;

  const categoriesResponse = await api.apiPublicGetCategoriesCategoriesGet();
  const categories = categoriesResponse.data as Category[];

  if (!player) {
    return <div>Joueur non trouvé</div>;
  }

  return (
      <PlayerFormComponent player={player} categories={categories} />
  );
}
