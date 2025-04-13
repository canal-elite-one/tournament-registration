"use client";

import { Text, Table } from "@mantine/core";
import { CategoryResult } from "@/backend_api/backend";

export default function CategoryTable({ categories, day }: {
  categories: CategoryResult[];
  day: string;
}) {
  return (
      <div className="rounded-lg overflow-hidden shadow-md mb-4 w-full max-w-3xl mx-auto">
        <Table.ScrollContainer minWidth={0}>
          <Table withColumnBorders withRowBorders highlightOnHover className="w-full">
            <Table.Thead>
              <Table.Tr>
                <Table.Th colSpan={7} className="bg-blue-950 p-2">
                  <Text c="white" fw={700} ta="center" size="sm">
                    {day}
                  </Text>
                </Table.Th>
              </Table.Tr>
              <Table.Tr>
                <Table.Th ta="center" className="w-1/12">Joueurs</Table.Th>
                <Table.Th ta="center" className="w-1/12">Tableaux</Table.Th>
                <Table.Th ta="center" className="w-2/12">Pointage</Table.Th>
                <Table.Th ta="center" className="w-3/12">Classement</Table.Th>
                <Table.Th ta="center" className="w-2/12">Vainqueur</Table.Th>
                <Table.Th ta="center" className="w-2/12">Finaliste</Table.Th>
                <Table.Th ta="center" className="w-2/12">1/2 Finaliste</Table.Th>
              </Table.Tr>
            </Table.Thead>

            <Table.Tbody>
              {categories.map((category) => {
                const categoryId = category.categoryId;

                return (
                    <Table.Tr key={categoryId}>
                      <Table.Td ta="center" className="text-sm">
                        {category.maxPlayers}
                      </Table.Td>

                      <Table.Td ta="center" className="text-sm">
                        {category.categoryId}
                      </Table.Td>

                      <Table.Td ta="center" className="text-sm">
                        <Text size="xs">
                          {category.startTime.getHours()}h
                          {category.startTime.getMinutes().toString().padStart(2, "0")}
                        </Text>
                      </Table.Td>

                      <Table.Td ta="center" className="text-sm truncate max-w-[120px]">
                        <Text size="xs">{category.alternateName}</Text>
                      </Table.Td>

                      <Table.Td ta="center" className="text-sm">
                        <Text size="xs">{category.rewardFirst} €</Text>
                      </Table.Td>
                      <Table.Td ta="center" className="text-sm">
                        <Text size="xs">{category.rewardSecond} €</Text>
                      </Table.Td>
                      <Table.Td ta="center" className="text-sm">
                        <Text size="xs">{category.rewardSemi} €</Text>
                      </Table.Td>
                    </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </div>
  );
}
