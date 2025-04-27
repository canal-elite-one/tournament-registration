import {DefaultApi} from "@/backend_api/backend";
import AdminPlayerForm from "@/app/admin/joueurs/[licenceNo]/AdminPlayerForm";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;

  const api = new DefaultApi();

  const response = await api.getAdminPlayerByLicenceNo({
    licenceNo: licenceNo,
  });

  const player = response.player;
  const entries = response.entries;

  const categories = await api.getCategories();

  return <AdminPlayerForm player={player} entries={entries} categories={categories} isPlayerFromDB={response.isPlayerFromDb}/>;
}
