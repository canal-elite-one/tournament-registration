"use client";

import {
  CategoryResult,
  FfttPlayer,
} from "@/backend_api/backend";
import { useState } from "react";
import {Table, Text, Checkbox, Group, Tooltip} from "@mantine/core";
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
      <div className="rounded-lg overflow-hidden shadow-md mb-4">
        <Table.ScrollContainer minWidth={500}>
          <Table withColumnBorders withRowBorders highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th colSpan={4} className="bg-blue-950">
                  <Text c="white" fw={700} p="sm" ta="center">
                    {day}
                  </Text>
                </Table.Th>
              </Table.Tr>
              <Table.Tr>
                <Table.Th ta="center" className="w-1/12">Tableau</Table.Th>
                <Table.Th ta="center" className="w-1/3">Classement</Table.Th>
                <Table.Th ta="center" className="w-1/6">Nombre de places restantes</Table.Th>
                <Table.Th ta="center" className="w-1/6">Inscription</Table.Th>
              </Table.Tr>
            </Table.Thead>

            <Table.Tbody>
              {categories.map((category) => {
                const categoryId = category.categoryId;
                const maxOverbooked = Math.floor(
                    category.maxPlayers * (1 + (category.overbookingPercentage ?? 0) / 100.0)
                );
                const entryCount = category.entryCount ?? 0;

                const isFull = entryCount > maxOverbooked + 40;
                const isInWaitingList = entryCount > maxOverbooked && entryCount <= maxOverbooked + 40;
                const isOutOfPointsRange =
                    player.nbPoints < category.minPoints || player.nbPoints > category.maxPoints;
                const isGenderMismatch = category.womenOnly && player.gender === "M";

                const disabled = isFull || isOutOfPointsRange || isGenderMismatch;

                const availableSpots = maxOverbooked - entryCount;

                let availabilityText =
                    availableSpots <= category.maxPlayers
                        ? `${availableSpots}`
                        : `${category.maxPlayers}`;
                let availabilityColor: string = "green";

                if (isFull) {
                  availabilityText = "Complet";
                  availabilityColor = "red";
                } else if (isInWaitingList) {
                  availabilityText = `Liste d'attente : ${entryCount - maxOverbooked + 1}e`;
                  availabilityColor = "yellow";
                }

                return (
                  <Table.Tr key={categoryId}>
                    {/* ID */}
                    <Table.Td ta="center" className="w-1/12" style={{ backgroundColor: category.color ?? undefined }}>
                      {categoryId}
                    </Table.Td>

                    {/* Name */}
                    <Table.Td ta="center" className="w-1/3">{category.alternateName}</Table.Td>

                    {/* Availability */}
                    <Table.Td ta="center" className="w-1/6">
                      <Text c={availabilityColor}>{availabilityText}</Text>
                    </Table.Td>

                    {/* Registration Checkbox */}
                    <Table.Td className="w-1/6">
                      <Group justify="center">
                        <Checkbox
                          id={`register-checkbox-${categoryId}`}
                          disabled={disabled}
                          checked={selectedCategories.includes(categoryId)}
                          onChange={() => toggleCategorySelection(categoryId)}
                        />
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </div>
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

    const response = await fetch("/api/player/register", {
      method: "POST",
      body: JSON.stringify({
        licenceNumber: player.licenceNo,
        email: email,
        phone: phone,
        selectedCategories: selectedCategories
      }),
    });

    if (response.ok) {
      const {amountToPay} = await response.json();
      if (amountToPay > 0) {
        await handleCheckout(player.licenceNo, amountToPay, email);
      } else {
        router.push(`/joueur/${player.licenceNo}/inscription`)
      }
    } else {
      const {error} = await response.json();
      console.log(`Error during ${player.licenceNo} registration:`, response.status, error);
      router.push("/error")
    }
  };

  // Calculate the number of selected entries per day
  const nbEntriesSaturday = selectedCategories.filter(categoryId =>
      saturdayCategories.some(category => category.categoryId === categoryId)
  ).length;

  const nbEntriesSunday = selectedCategories.filter(categoryId =>
      sundayCategories.some(category => category.categoryId === categoryId)
  ).length;

  // Define your limits
  const maxEntriesPerDaySaturday = 2; // replace with your actual limit
  const maxEntriesPerDaySunday = 2; // replace with your actual limit

  // Determine button state and tooltip
  let isSubmitDisabled = false;
  let submitTooltip = "";

  if (nbEntriesSaturday > maxEntriesPerDaySaturday) {
    isSubmitDisabled = true;
    submitTooltip = `Vous ne pouvez pas vous inscrire à plus de ${maxEntriesPerDaySaturday} tableaux pour la journée de samedi.`;
  } else if (nbEntriesSunday > maxEntriesPerDaySunday) {
    isSubmitDisabled = true;
    submitTooltip = `Vous ne pouvez pas vous inscrire à plus de ${maxEntriesPerDaySunday} tableaux pour la journée de dimanche.`;
  } else if (nbEntriesSaturday + nbEntriesSunday === 0) {
    isSubmitDisabled = true;
    submitTooltip = "Vous devez vous inscrire à au moins un tableau.";
  }

  return (
      <div className="flex flex-col lg:flex-row justify-between gap-4">
        {/* Left Column (Tables) */}
        <div className="w-full lg:w-1/2 p-4 relative">
          <h2 className="text-lg font-bold mb-4">Tableaux</h2>

          {/* Saturday Table */}
          {saturdayCategories.length > 0 && generateCategoriesTable(saturdayCategories, "Samedi")}

          {/* Sunday Table */}
          {sundayCategories.length > 0 && generateCategoriesTable(sundayCategories, "Dimanche")}
        </div>

        {/* Right Column (Form) */}
        <div className="w-full lg:w-1/2 p-4">
          <div className="w-full mx-auto bg-white shadow-md rounded-md overflow-hidden">
            <form className="px-6 py-4" onSubmit={handleSubmit}>
              <div className="font-bold text-xl mb-4">Inscription</div>

              {/* Name Fields */}
              <div className="mb-4 flex flex-col sm:flex-row gap-4">
                <div className="w-full sm:w-1/2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Prénom</label>
                  <input
                      disabled
                      value={player.firstName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-full sm:w-1/2">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Nom</label>
                  <input
                      disabled
                      value={player.lastName}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
              </div>

              {/* Licence, Points, Gender */}
              <div className="mb-4 flex flex-col sm:flex-row gap-4">
                <div className="w-full sm:w-1/3">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Numéro de licence</label>
                  <input
                      disabled
                      value={player.licenceNo}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-full sm:w-1/3">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Classement</label>
                  <input
                      disabled
                      value={player.nbPoints}
                      className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                      type="text"
                  />
                </div>
                <div className="w-full sm:w-1/3">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Sexe</label>
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
                <label className="block text-gray-700 text-sm font-bold mb-2">Club</label>
                <input
                    disabled
                    value={player.club}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="text"
                />
              </div>

              {/* Email */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">Adresse email</label>
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
                <label className="block text-gray-700 text-sm font-bold mb-2">Numéro de téléphone</label>
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
              <div className="flex flex-col items-end mt-auto">
                <Tooltip label={submitTooltip} disabled={!isSubmitDisabled} withArrow position="top">
                  <button
                      id="submit-button"
                      type="submit"
                      className={`transition-all duration-300 ease-in-out bg-blue-950 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${
                          isSubmitDisabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
                      }`}
                      disabled={isSubmitDisabled}
                  >
                    S&rsquo;inscrire
                  </button>
                </Tooltip>

                {isSubmitDisabled && (
                    <p className="text-red-600 text-sm mt-2 text-right">{submitTooltip}</p>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
  );
}
