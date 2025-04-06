import {Category, DefaultApi, Player} from "@/backend_api/backend";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const licenceNo = (await params).licenceNo;

  const api = new DefaultApi();
  const playerResponse = await api.apiPublicGetPlayerPlayersLicenceNoGet(licenceNo)
  const player = playerResponse.data as Player;

  const categoriesResponse = await api.apiPublicGetCategoriesCategoriesGet();
  const categories = categoriesResponse.data as Category[];

  categories.forEach((category) => {
    console.log(category);
  })

  if (!player) {
    return <div>Joueur non trouvé</div>;
  }

  return (
      <div>
        <div key="recap">
          <h1 className="text-2xl font-bold">Joueur {licenceNo}</h1>
          <p>{player.firstName} {player.lastName}</p>
        </div>
      </div>
  );
}
