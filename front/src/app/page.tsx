import {DefaultApi} from "@/backend_api/backend";
import PlayerSearch from "@/components/PlayerSearch";
import CategoryTable from "@/components/CategoryTable";
import CountDownPage from "@/components/CountDownPage";

export default async function HomePage() {

  const startDate = process.env.REGISTRATION_START_DATE || new Date();
  const targetDate = new Date(startDate);
  const now = new Date();

  const isRegistrationOpen = (targetDate.getTime() - now.getTime()) <= 0;

  const api = new DefaultApi();
  const categories = await api.getCategories();

  const saturdayCategories = categories.filter((category) => {
    const startTime = new Date(category.startTime);
    return startTime.getDay() === 6; // 6 corresponds to Saturday
  });

  const sundayCategories = categories.filter((category) => {
    const startTime = new Date(category.startTime);
    return startTime.getDay() === 0; // 0 corresponds to Sunday
  });

  if (isRegistrationOpen) {
    return (
        <div className="flex flex-col items-center gap-16 pt-8 bg-gray-50 min-h-screen">
          <PlayerSearch />
          <CategoryTable categories={saturdayCategories} day="Samedi" />
          <CategoryTable categories={sundayCategories} day="Dimanche" />
        </div>
    );
  } else {
    return <CountDownPage startDate={targetDate}/>
  }
}
