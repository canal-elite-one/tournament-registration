"use client";

import {
  CategoryResult, EntryWithCategory,
  Player,
} from "@/backend_api/backend";
import { useState } from "react";
import {Table, Text, Checkbox, Group, Tooltip, Modal} from "@mantine/core";
import {useRouter} from "next/navigation";

export default function AdminPlayerForm({
                                              player,
                                              entries,
                                              categories,
                                              isPlayerFromDB
                                            }: {
  player: Player;
  entries: EntryWithCategory[];
  categories: CategoryResult[];
  isPlayerFromDB: boolean;
}) {

  const [email, setEmail] = useState(player.email);
  const [phone, setPhone] = useState(player.phone ?? "");
  const [selectedCategories, setSelectedCategories] = useState<string[]>(entries.map(entry => entry.categoryId));
  const [paidCategories, setPaymentSelection] = useState<string[]>(entries.filter(e => e.markedAsPaid).map(entry => entry.categoryId));
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

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

  const togglePaymentSelection = (categoryId: string) => {
    setPaymentSelection((prevSelected) =>
        prevSelected.includes(categoryId)
            ? prevSelected.filter((id) => id !== categoryId)
            : [...prevSelected, categoryId]
    );
  };

  const generateCategoriesTable = (categories: CategoryResult[], entries: EntryWithCategory[], day: string) => {
    return (
        <div className="rounded-lg overflow-hidden shadow-md mb-4">
          <Table.ScrollContainer minWidth={500}>
            <Table withColumnBorders withRowBorders highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th colSpan={6} className="bg-blue-950">
                    <Text c="white" fw={700} p="sm" ta="center">
                      {day}
                    </Text>
                  </Table.Th>
                </Table.Tr>
                <Table.Tr>
                  <Table.Th ta="center" className="w-1/15">Tableau</Table.Th>
                  <Table.Th ta="center" className="w-7/15">Classement</Table.Th>
                  <Table.Th ta="center" className="w-3/15">Nombre de places restantes</Table.Th>
                  <Table.Th ta="center" className="w-1/15">Rank</Table.Th>
                  <Table.Th ta="center" className="w-2/15">Inscription</Table.Th>
                  <Table.Th ta="center" className="w-1/15">Payer</Table.Th>
                </Table.Tr>
              </Table.Thead>

              <Table.Tbody>
                {categories.map((category) => {
                  const categoryId = category.categoryId;
                  const maxOverbooked = Math.floor(
                      category.maxPlayers * (1 + (category.overbookingPercentage ?? 0) / 100.0)
                  );
                  const entryCount = category.entryCount ?? 0;

                  const categoryEntry = entries.find(entry => entry.categoryId === categoryId);

                  let rank = entryCount;
                  if (categoryEntry) {
                    rank = categoryEntry.rank;
                  }

                  const isFull = entryCount > maxOverbooked + 40;
                  const isInWaitingList = entryCount > maxOverbooked && entryCount <= maxOverbooked + 40;
                  const isOutOfPointsRange =
                      player.nbPoints < category.minPoints || player.nbPoints > category.maxPoints;
                  const isGenderMismatch = category.womenOnly && player.gender === "M";

                  const disabled = isOutOfPointsRange || isGenderMismatch;

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
                        <Table.Td ta="center" className="w-1/15" style={{ backgroundColor: category.color ?? undefined }}>
                          {categoryId}
                        </Table.Td>

                        {/* Name */}
                        <Table.Td ta="center" className="w-7/15">{category.alternateName}</Table.Td>

                        {/* Availability */}
                        <Table.Td ta="center" className="w-3/15">
                          <Text c={availabilityColor}>{availabilityText}</Text>
                        </Table.Td>

                        {/* Rank */}
                        <Table.Td ta="center" className="w-1/15">
                          <Text>{rank}</Text>
                        </Table.Td>

                        {/* Registration Checkbox */}
                        <Table.Td className="w-2/15">
                          <Group justify="center">
                            <Checkbox
                                id={`register-checkbox-${categoryId}`}
                                disabled={disabled}
                                checked={selectedCategories.includes(categoryId)}
                                onChange={() => toggleCategorySelection(categoryId)}
                            />
                          </Group>
                        </Table.Td>

                        {/* Payment Checkbox */}
                        <Table.Td className="w-1/15">
                          <Group justify="center">
                            <Checkbox
                                id={`payment-checkbox-${categoryId}`}
                                checked={paidCategories.includes(categoryId)}
                                onChange={() => togglePaymentSelection(categoryId)}
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

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const entryInfo = selectedCategories.map((categoryId) => {
      const entry = entries.find(entry => entry.categoryId === categoryId);
      return {
        categoryId: categoryId,
        markedAsPaid: paidCategories.includes(categoryId),
        markedAsPresent: entry?.markedAsPresent ?? null,
      }
    });

    console.log(entryInfo);

    const response = await fetch("/api/admin/player/register", {
      method: "POST",
      body: JSON.stringify({
        licenceNo: player.licenceNo,
        email: email,
        phone: phone,
        isPlayerFromDB: isPlayerFromDB,
        totalActualPaid: player.totalActualPaid,
        entryInfo: entryInfo
      }),
    });

    if (response.ok) {
      router.push(`/admin/joueurs`)
    } else {
      const {error} = await response.json();
      console.log(`Error during ${player.licenceNo} registration:`, response.status, error);
      router.push("/error")
    }
  };

  // Determine button state and tooltip
  const isSubmitDisabled = false;
  const submitTooltip = "";

  return (
      <div className="flex flex-col lg:flex-row justify-between gap-4">
        {/* Left Column (Tables) */}
        <div className="w-full lg:w-1/2 p-4 relative">
          <h2 className="text-lg font-bold mb-4">Tableaux</h2>

          {/* Saturday Table */}
          {saturdayCategories.length > 0 && generateCategoriesTable(saturdayCategories, entries, "Samedi")}

          {/* Sunday Table */}
          {sundayCategories.length > 0 && generateCategoriesTable(sundayCategories, entries, "Dimanche")}
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
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight"
                    type="tel"
                    placeholder="Votre numéro de téléphone"
                />
              </div>

              {/* Submit Button */}
              <div className="flex flex-col items-end mt-auto">
                <div className="flex justify-end w-full gap-4">
                  {/* Delete Button */}
                  <button
                      type="button"
                      className="transition-all duration-300 ease-in-out bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                      onClick={() => setDeleteModalOpen(true)}
                  >
                    Supprimer
                  </button>

                  {/* Submit Button */}
                  <Tooltip label={submitTooltip} disabled={!isSubmitDisabled} withArrow position="top">
                    <button
                        id="submit-button"
                        type="submit"
                        className={`transition-all duration-300 ease-in-out bg-blue-950 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${
                            isSubmitDisabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
                        }`}
                        disabled={isSubmitDisabled}
                    >
                      Inscrire
                    </button>
                  </Tooltip>
                </div>

                {isSubmitDisabled && (
                    <p className="text-red-600 text-sm mt-2 text-right">{submitTooltip}</p>
                )}
              </div>

            </form>
          </div>
        </div>

        <Modal
            opened={deleteModalOpen}
            onClose={() => setDeleteModalOpen(false)}
            title="Confirmer la suppression"
            centered
        >
          <Text>Êtes-vous sûr de vouloir supprimer ce joueur ? Cette action est irréversible.</Text>

          <div className="flex justify-end gap-4 mt-6">
            <button
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
                onClick={() => setDeleteModalOpen(false)}
            >
              Annuler
            </button>
            <button
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                onClick={async () => {
                  const response = await fetch(`/api/admin/player/delete`, {
                    method: "DELETE",
                    body: JSON.stringify({ licenceNo: player.licenceNo }),
                    headers: {
                      "Content-Type": "application/json",
                    },
                  });

                  if (response.ok) {
                    router.push("/admin/joueurs");
                  } else {
                    console.error("Failed to delete player");
                    setDeleteModalOpen(false);
                  }
                }}
            >
              Supprimer
            </button>
          </div>
        </Modal>

      </div>
  );
}
