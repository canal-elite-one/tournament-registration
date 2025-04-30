"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Table, Text, Badge, SegmentedControl, Group } from "@mantine/core";
import { AdminPlayer } from "@/backend_api/backend"; // Adjust import path as needed

export default function AdminPlayersTable({ players }: { players: AdminPlayer[] }) {
  const [filter, setFilter] = useState<"all" | "paid" | "unpaid">("all");

  const router = useRouter();


  type SortField = "firstName" | "lastName" | "licenceNo" | "club";
  type SortDirection = "asc" | "desc";

  const [sortBy, setSortBy] = useState<SortField>("lastName");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const toggleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortDirection("asc");
    }
  };

  const filteredPlayers = players
      .filter((player) => {
        if (filter === "paid") return player.remainingAmount === 0;
        if (filter === "unpaid") return player.remainingAmount > 0;
        return true;
      })
      .sort((a, b) => {
        const aValue = a[sortBy]?.toString().toLowerCase();
        const bValue = b[sortBy]?.toString().toLowerCase();

        if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
        if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
        return 0;
      });



  return (
      <div className="rounded-lg overflow-hidden shadow-md bg-white p-4">
        {/* Filter controls */}
        <Group justify="end" mb="md">
          <SegmentedControl
              value={filter}
              onChange={(val) => setFilter(val as "all" | "paid" | "unpaid")}
              data={[
                { label: "Tous", value: "all" },
                { label: "Payés", value: "paid" },
                { label: "Non payés", value: "unpaid" },
              ]}
          />
        </Group>

        {/* Table */}
        <Table.ScrollContainer minWidth={600}>
          <Table striped withColumnBorders withRowBorders>
            <Table.Thead className="[&>tr:hover]:bg-blue-950">
              <Table.Tr className="bg-blue-950">
                <Table.Th ta="center" onClick={() => toggleSort("lastName")} className="cursor-pointer">
                  <Text c="white" fw={600}>
                    Nom {sortBy === "lastName" && (sortDirection === "asc" ? "↑" : "↓")}
                  </Text>
                </Table.Th>
                <Table.Th ta="center" onClick={() => toggleSort("firstName")} className="cursor-pointer">
                  <Text c="white" fw={600}>
                    Prénom {sortBy === "firstName" && (sortDirection === "asc" ? "↑" : "↓")}
                  </Text>
                </Table.Th>
                <Table.Th ta="center" onClick={() => toggleSort("licenceNo")} className="cursor-pointer">
                  <Text c="white" fw={600}>
                    Licence {sortBy === "licenceNo" && (sortDirection === "asc" ? "↑" : "↓")}
                  </Text>
                </Table.Th>
                <Table.Th ta="center" onClick={() => toggleSort("club")} className="cursor-pointer">
                  <Text c="white" fw={600}>
                    Club {sortBy === "club" && (sortDirection === "asc" ? "↑" : "↓")}
                  </Text>
                </Table.Th>
                <Table.Th ta="center"><Text c="white" fw={600}>Payé</Text></Table.Th>
                <Table.Th ta="center"><Text c="white" fw={600}>Montant restant (€)</Text></Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {filteredPlayers.map((player) => (
                  <Table.Tr
                      key={player.licenceNo}
                      onClick={() => router.push(`/admin/joueurs/${player.licenceNo}`)}
                      className="cursor-pointer hover:bg-gray-100 transition-colors"
                  >

                  <Table.Td>{player.lastName}</Table.Td>
                    <Table.Td>{player.firstName}</Table.Td>
                    <Table.Td>{player.licenceNo}</Table.Td>
                    <Table.Td>{player.club}</Table.Td>
                    <Table.Td className="text-center">
                      {player.remainingAmount === 0 ? (
                          <Badge color="green" variant="light">Payé</Badge>
                      ) : (
                          <Badge color="red" variant="light">Non payé</Badge>
                      )}
                    </Table.Td>
                    <Table.Td>{player.remainingAmount.toFixed(2)}</Table.Td>
                  </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </div>
  );
}
