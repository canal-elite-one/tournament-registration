import {DefaultApi} from "@/backend_api/backend";
import {round} from "@floating-ui/utils";
import CategoryMetricsTable from "@/components/CategoryMetricsTable";

export const dynamic = "force-dynamic";


export interface CategoryMetrics {
  categoryId: string;
  alternateName: string | null;
  numberOfEntries: number;
  numberInWaitingList: number;
  numberOfPaidEntries: number;
  fillRate: number;
}

export default async function AdminDashboard() {

  const api = new DefaultApi();
  const entriesByCategoryResponse = await api.getEntriesByCategory({presentOnly: false});

  const categories = await api.getCategories();

  const categoryMetrics: CategoryMetrics[] = [];

  // count total number of entries by category
  for (const [categoryId, entries] of Object.entries(entriesByCategoryResponse.entriesByCategory)) {
    const category = categories.find(c => c.categoryId === categoryId);
    if (!category) {
      console.error(`Category ${categoryId} not found`);
      continue;
    }

    const maxOverbooked = Math.floor(category?.maxPlayers * (1 + category?.overbookingPercentage / 100.0));

    const metrics = {
      categoryId: categoryId,
      alternateName: category?.alternateName,
      numberOfEntries: entries.length,
      numberInWaitingList: entries.length > maxOverbooked ? entries.length - maxOverbooked : 0,
      numberOfPaidEntries: entries.filter(e => e.markedAsPaid).length,
      fillRate: round((entries.length / maxOverbooked) * 100),
    }

    categoryMetrics.push(metrics);
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <CategoryMetricsTable categoryMetrics={categoryMetrics} />
    </div>
  );
}
