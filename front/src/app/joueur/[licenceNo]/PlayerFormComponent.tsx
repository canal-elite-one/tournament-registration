"use client";

import {
  CategoryResult,
  DefaultApi, FfttPlayer,
  RegisterEntriesRequest
} from "@/backend_api/backend";
import { useState } from "react";
import {Table, Text, Checkbox, Group} from "@mantine/core";
import {notifications} from "@mantine/notifications";
import {useRouter} from "next/navigation";

export default function PlayerFormComponent({
                                              player,
                                              categories,
                                            }: {
  player: FfttPlayer;
  categories: CategoryResult[];
}) {

  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const router = useRouter();



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
        <Table withColumnBorders withRowBorders highlightOnHover>
          <thead>
          <tr>
            <th colSpan={4}>
              <Text c="white" fw={700} bg="blue.9" p="sm" ta="center">
                {day}
              </Text>
            </th>
          </tr>
          <tr>
            <th>ID</th>
            <th>Nom</th>
            <th>Nombre de places restantes</th>
            <th>Inscription</th>
          </tr>
          </thead>
          <tbody>
          {categories.map((category) => {
            const categoryId = category.categoryId;
            const maxOverbooked = Math.floor(category.maxPlayers * (1 + (category.overbookingPercentage ?? 0) / 100.0));
            const entryCount = category.entryCount ?? 0;

            const isFull = entryCount > maxOverbooked + 40;
            const isInWaitingList = entryCount > maxOverbooked && entryCount <= maxOverbooked + 40;
            const isOutOfPointsRange = player.nbPoints < category.minPoints || player.nbPoints > category.maxPoints;
            const isGenderMismatch = category.womenOnly && player.gender === "M";

            const disabled = isFull || isOutOfPointsRange || isGenderMismatch;

            const availableSpots = maxOverbooked - entryCount;

            let availabilityText = availableSpots <= category.maxPlayers ? `${availableSpots}` : `${category.maxPlayers}`;
            let availabilityColor: string = "green";

            if (isFull) {
              availabilityText = "Complet";
              availabilityColor = "red";
            } else if (isInWaitingList) {
              availabilityText = `Liste d'attente : ${entryCount - maxOverbooked + 1}e`;
              availabilityColor = "yellow";
            }

            return (
                <tr key={categoryId}>
                  {/* ID */}
                  <td style={{ backgroundColor: category.color ?? undefined }}>
                    {categoryId}
                  </td>

                  {/* Name */}
                  <td>{category.alternateName}</td>

                  {/* Availability */}
                  <td>
                    <Text c={availabilityColor}>{availabilityText}</Text>
                  </td>

                  {/* Registration Checkbox */}
                  <td>
                    <Group justify="center">
                      <Checkbox
                          id={`register-checkbox-${categoryId}`}
                          disabled={disabled}
                          checked={selectedCategories.includes(categoryId)}
                          onChange={() => toggleCategorySelection(categoryId)}
                      />
                    </Group>
                  </td>
                </tr>
            );
          })}
          </tbody>
        </Table>
    );
  };

  const handleCheckout = async (licenceNo: string, amount: number, email: string) => {
    try {
      const response = await fetch("/api/create-checkout-session", {
        method: "POST",
        body: JSON.stringify({
          licenceNumber: licenceNo,
          amount: amount,
          customerEmail: email,
        }),
      });

      const data = await response.json();

      if (data.url) {
        router.push(data.url);
        window.location.href = data.url;
      } else {
        notifications.show({
          title: "Error",
          message: "Could not create checkout session",
          color: "red",
        });
      }
    } catch (error: any) {
      notifications.show({
        title: "Error",
        message: error.message,
        color: "red",
      });
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const api = new DefaultApi();

    const registrationRequest: RegisterEntriesRequest = {
      licenceNo: player.licenceNo,
      registerEntriesBody: {
        contactInfo: {
          email: email,
          phone: phone,
        },
        categoryIds: selectedCategories
      },
    }

    try {
      const registeredEntries = await api.registerEntries(registrationRequest);
      await handleCheckout(player.licenceNo, registeredEntries.amountToPay, email);
    } catch(error) {
      const response = error.response;
      const body = await response?.json();
      console.error(body);
    }
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
