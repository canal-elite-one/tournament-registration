"use client";

import { CategoryResult, Player } from "@/backend_api/backend";
import { useState } from "react";

export default function PlayerFormComponent({
                                              player,
                                              categories,
                                            }: {
  player: Player;
  categories: CategoryResult[];
}) {
  const [email, setEmail] = useState(player.email);
  const [phone, setPhone] = useState(player.phone || "");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);


  // Split categories by day
  const saturdayCategories = categories.filter(category =>
      new Date(category.startTime).getDay() === 6 // Saturday
  );

  const sundayCategories = categories.filter(category =>
      new Date(category.startTime).getDay() === 0 // Sunday
  );

  const toggleCategorySelection = (categoryId: string) => {
    setSelectedCategories((prevSelected) =>
        prevSelected.includes(categoryId)
            ? prevSelected.filter((id) => id !== categoryId)
            : [...prevSelected, categoryId]
    );
  };

  const generateCategoriesTable = (categories: CategoryResult[], day: string) => {
    return (
        <table className="w-full border mb-4">
          <thead className="bg-blue-950 rounded-t-lg">
          <tr>
            <th colSpan={6} className="text-white">${day}</th>
          </tr>
          <tr>
            <th className="text-white">ID</th>
            <th className="text-white">Nom</th>
            <th className="text-white">Nombre de place restantes</th>
            <th className="text-white">Inscription</th>
          </tr>
          </thead>
          <tbody>
          {categories.map(category => {
            const categoryId = category.categoryId;
            const maxOverbooked = Math.floor(category.maxPlayers * (1 + (category.overbookingPercentage ?? 0) / 100.0));
            // FixME when entryCount in category
            const entryCount = category.entryCount ?? 0;

            const isFull = entryCount > maxOverbooked + 40;
            const isInWaitingList = entryCount > maxOverbooked && entryCount <= maxOverbooked + 40;
            const isOutOfPointsRange = player.nbPoints < category.minPoints || player.nbPoints > category.maxPoints;
            const isGenderMismatch = category.womenOnly && player.gender === "M";

            const disabled = isFull || isOutOfPointsRange || isGenderMismatch;

            let availabilityText = "Oui";
            let availabilityClass = "text-green-600";

            if (isOutOfPointsRange) {
              availabilityText = "Non éligible (points)";
              availabilityClass = "text-red-600";
            } else if (isGenderMismatch) {
              availabilityText = "Non éligible (genre)";
              availabilityClass = "text-red-600";
            } else if (isFull) {
              availabilityText = "Complet";
              availabilityClass = "text-red-600";
            } else if (isInWaitingList) {
              availabilityText = `Position ${entryCount - maxOverbooked + 1} en liste d'attente`;
              availabilityClass = "text-yellow-600";
            }

            return (
                <tr key={categoryId}>
                  {/* ID */}
                  <td
                      className="border px-4 py-2"
                      style={{ backgroundColor: category.color ?? undefined }}
                  >
                    {categoryId}
                  </td>

                  {/* Name */}
                  <td className="border px-4 py-2">{category.alternateName}</td>

                  {/* Availability */}
                  <td className={`border px-4 py-2 ${availabilityClass}`}>
                    {availabilityText}
                  </td>

                  {/* Registration Checkbox */}
                  <td className={`border px-4 py-2 ${disabled ? "opacity-50" : ""}`}>
                    <input
                        type="checkbox"
                        id={`register-checkbox-${categoryId}`}
                        disabled={disabled}
                        checked={selectedCategories.includes(categoryId)}
                        onChange={() => toggleCategorySelection(categoryId)}
                    />
                    <label htmlFor={`register-checkbox-${categoryId}`}> </label>
                  </td>
                </tr>
            );
          })}

          </tbody>
        </table>
    )};


  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    console.log("Submitting form with:", { email, phone });
    // TODO: connect with your API for submission
  };

  return (
      <div className="flex justify-between">
        {/* Left Column */}
        <div className="w-1/2 p-4">
          <div className="w-full mx-auto bg-white shadow-md rounded-md overflow-hidden">
            <form className="px-6 py-4" onSubmit={handleSubmit}>
              <div className="font-bold text-xl mb-2">Inscription</div>

              {/* Name Fields */}
              <div className="mb-4 flex">
                <div className="w-1/2 pr-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Prénom
                  </label>
                  <input
                      disabled
                      value={player.firstName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/2 pl-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Nom
                  </label>
                  <input
                      disabled
                      value={player.lastName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
              </div>

              {/* Licence, Points, Gender */}
              <div className="mb-4 flex">
                <div className="w-1/3 pr-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Numéro de licence
                  </label>
                  <input
                      disabled
                      value={player.licenceNo}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/3 px-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Classement
                  </label>
                  <input
                      disabled
                      value={player.nbPoints}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-1/3 pl-2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Sexe
                  </label>
                  <input
                      disabled
                      value={player.gender}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
              </div>

              {/* Club */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Club
                </label>
                <input
                    disabled
                    value={player.club}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="text"
                />
              </div>

              {/* Email */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Adresse email
                </label>
                <input
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="email"
                    placeholder="Votre adresse courriel"
                />
              </div>

              {/* Phone */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Numéro de téléphone
                </label>
                <input
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="tel"
                    placeholder="Votre numéro de téléphone"
                />
              </div>

              {/* Submit Button */}
              <div className="flex mt-auto">
                <button
                    type="submit"
                    className={`bg-blue-950 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4 ml-auto ${
                        selectedCategories.length === 0 ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                    disabled={selectedCategories.length === 0}
                >
                  S&lsquo;inscrire
                </button>

              </div>
            </form>
          </div>
        </div>

        {/* Right Column (Tables) */}
        <div className="w-1/2 p-4 relative">
          <h2 className="text-lg font-bold mb-4">Tableaux</h2>

          {/* Saturday Table */}
          {saturdayCategories.length > 0 && generateCategoriesTable(saturdayCategories, "Samedi")}

          {/* Sunday Table */}
          {sundayCategories.length > 0 && generateCategoriesTable(sundayCategories, "Dimanche")}
        </div>
      </div>
  );
}
