import {DefaultApi} from "@/backend_api/backend";
import EntriesByCategoryTabs from "@/components/EntriesByCategoryTabs";

export const dynamic = "force-dynamic";


export default async function AdminPlayersByCategoriesPage() {

  const api = new DefaultApi();
  const entriesByCategoryResponse = await api.getEntriesByCategory({presentOnly: false});

  return (
      <div>
        <h1 className="text-2xl font-semibold">Joueurs par tableaux</h1>
        <EntriesByCategoryTabs entriesByCategory={entriesByCategoryResponse.entriesByCategory} />
      </div>
  );
};
