"use client";

import {Tabs, Table, Badge, TextInput} from "@mantine/core";
import { Spotlight, SpotlightActionData, openSpotlight } from "@mantine/spotlight";
import { useMemo, useState } from "react";
import {useRouter} from "next/navigation";

interface EntryWithPlayer {
  categoryId: string;
  licenceNo: string;
  color: string | null;
  registrationTime: Date | null;
  markedAsPresent: boolean | null;
  markedAsPaid: boolean;
  firstName: string;
  lastName: string;
  club: string;
  gender: string;
  nbPoints: number;
  bibNo?: number | null;
  email: string;
  phone: string | null;
  totalActualPaid: number | null;
}

interface Props {
  entriesByCategory: { [key: string]: EntryWithPlayer[] };
}

export default function EntriesByCategoryTabs({ entriesByCategory }: Props) {
  const categoryIds = Object.keys(entriesByCategory);
  const [activeTab, setActiveTab] = useState<string>(categoryIds[0]);
  const [search, setSearch] = useState<string>("");
  const router = useRouter();

  const allEntries = useMemo(() => Object.values(entriesByCategory).flat(), [entriesByCategory]);

  const spotlightActions: SpotlightActionData[] = allEntries.map((entry) => ({
    id: `${entry.categoryId}-${entry.licenceNo}`,
    label: `${entry.firstName} ${entry.lastName} (${entry.licenceNo})`,
    description: `${entry.club} — ${entry.categoryId}`,
    onClick: () => {
      setActiveTab(entry.categoryId);
      setSearch(entry.licenceNo); // autofill search to locate player faster
    },
  }));

  function goToPlayer() {
    router.push(`/admin/joueurs/${search}`);
  }


  const filteredEntries = (entries: EntryWithPlayer[]) => {
    if (!search.trim()) return entries;
    const searchLower = search.toLowerCase();
    return entries.filter((entry) =>
        [
          entry.licenceNo,
          entry.firstName,
          entry.lastName,
          entry.club,
          entry.email,
          entry.phone,
        ]
            .filter(Boolean)
            .some((field) => field?.toString().toLowerCase().includes(searchLower))
    );
  };

  const getBadgeColor = (value: boolean | null) => (value ? "green" : "red");

  return (
      <div className="p-4">
        {/* Sticky Search Bar */}
        <div className="sticky top-0 z-10 bg-white p-4 shadow-sm">
          <div className="flex justify-between items-center gap-4">
            <TextInput
                placeholder="Rechercher un joueur..."
                value={search}
                onChange={(e) => setSearch(e.currentTarget.value)}
                className="w-full max-w-md"
            />
            <button
                onClick={() => goToPlayer()}
                className="hidden sm:block bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded"
            >
              Ajouter
            </button>
            <button
                onClick={openSpotlight}
                className="hidden sm:block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              🔍 Cmd + K
            </button>
          </div>
        </div>

        {/* Tabs and Tables */}
        <Tabs value={activeTab}
              onChange={(value) => value && setActiveTab(value)}>
          <Tabs.List>
            {categoryIds.map((categoryId) => (
                <Tabs.Tab key={categoryId} value={categoryId}>
                  {categoryId}
                </Tabs.Tab>
            ))}
          </Tabs.List>

          {categoryIds.map((categoryId) => (
              <Tabs.Panel key={categoryId} value={categoryId} pt="md">
                <div className="overflow-x-auto rounded-lg mt-4">
                  <Table.ScrollContainer minWidth={900}>
                    <Table
                        withColumnBorders
                        withRowBorders
                        highlightOnHover
                        striped
                        className="w-full"
                    >
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>N° Dossard</Table.Th>
                          <Table.Th>Licence</Table.Th>
                          <Table.Th>Nom</Table.Th>
                          <Table.Th>Prénom</Table.Th>
                          <Table.Th>Club</Table.Th>
                          <Table.Th>Points</Table.Th>
                          <Table.Th>Sexe</Table.Th>
                          <Table.Th className="text-center">Présent</Table.Th>
                          <Table.Th className="text-center">Payé</Table.Th>
                          <Table.Th className="text-center">Date d&apos;inscription</Table.Th>
                        </Table.Tr>
                      </Table.Thead>

                      <Table.Tbody>
                        {filteredEntries(entriesByCategory[categoryId]).map((entry) => (
                            <Table.Tr key={entry.licenceNo}
                                      className="cursor-pointer hover:bg-gray-100 transition"
                                      onClick={() => router.push(`/admin/joueurs/${entry.licenceNo}`)}
                            >
                              <Table.Td>{entry.bibNo ?? "-"}</Table.Td>
                              <Table.Td>{entry.licenceNo}</Table.Td>
                              <Table.Td>{entry.lastName}</Table.Td>
                              <Table.Td>{entry.firstName}</Table.Td>
                              <Table.Td>{entry.club}</Table.Td>
                              <Table.Td>{entry.nbPoints}</Table.Td>
                              <Table.Td>{entry.gender}</Table.Td>
                              <Table.Td className="text-center">
                                <Badge color={getBadgeColor(entry.markedAsPresent)} variant="light">
                                  {entry.markedAsPresent ? "Présent" : "Absent"}
                                </Badge>
                              </Table.Td>
                              <Table.Td className="text-center">
                                <Badge color={getBadgeColor(entry.markedAsPaid)} variant="light">
                                  {entry.markedAsPaid ? "Payé" : "Non payé"}
                                </Badge>
                              </Table.Td>
                              <Table.Td className="text-center">
                                {entry.registrationTime
                                    ? new Date(entry.registrationTime).toLocaleString("fr-FR")
                                    : "-"}
                              </Table.Td>
                            </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </Table.ScrollContainer>
                </div>
              </Tabs.Panel>
          ))}
        </Tabs>

        {/* Spotlight Component */}
        <Spotlight
            actions={spotlightActions}
            nothingFound="Aucun résultat"
            shortcut="mod + K"
            highlightQuery
            scrollable
        />
      </div>
  );
}
