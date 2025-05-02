import {DefaultApi} from "@/backend_api/backend";
import AdminAllPlayersTable from "@/components/AdminAllPlayersTable";

export const dynamic = "force-dynamic";


export default async function AdminPlayersPage() {

  const api = new DefaultApi();
  const allPlayersResponse = await api.getAllPlayers({presentOnly: false});

  return (
    <div>
      <h1 className="text-2xl font-semibold">Tous les joueurs</h1>
      <AdminAllPlayersTable players={allPlayersResponse.players} />
    </div>
  );
};
