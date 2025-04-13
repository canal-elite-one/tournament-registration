"use client";

import {Text, Table} from "@mantine/core";
import {CategoryResult} from "@/backend_api/backend";

export default function CategoryTable({categories, day}: {
  categories: CategoryResult[];
  day: string;
}) {
  return (
      <div className="rounded-lg overflow-hidden shadow-md mb-4">
        <Table.ScrollContainer minWidth={500}>
          <Table withColumnBorders withRowBorders highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th colSpan={7} className="bg-blue-950">
                  <Text c="white" fw={700} p="sm" ta="center">
                    {day}
                  </Text>
                </Table.Th>
              </Table.Tr>
              <Table.Tr>
                <Table.Th ta="center">Joueurs</Table.Th>
                <Table.Th ta="center">Tableaux</Table.Th>
                <Table.Th ta="center">Fin de pointage</Table.Th>
                <Table.Th ta="center">Classement</Table.Th>
                <Table.Th ta="center">Vainqueur</Table.Th>
                <Table.Th ta="center">Finaliste</Table.Th>
                <Table.Th ta="center">1/2 Finaliste</Table.Th>
              </Table.Tr>
            </Table.Thead>

            <Table.Tbody>
              {categories.map((category) => {
                const categoryId = category.categoryId;

                return (
                    <Table.Tr key={categoryId}>
                      <Table.Td ta="center">
                        {category.maxPlayers}
                      </Table.Td>

                      <Table.Td ta="center">{category.categoryId}</Table.Td>

                      <Table.Td ta="center">
                        <Text>{category.startTime.getHours()}h{category.startTime.getMinutes().toString().padStart(2, '0')}</Text>
                      </Table.Td>

                      <Table.Td ta="center">
                        <Text>{category.alternateName}</Text>
                      </Table.Td>

                      {/* Prizes */}
                      <Table.Td ta="center">
                        <Text>{category.rewardFirst} &euro;</Text>
                      </Table.Td>
                      <Table.Td ta="center">
                        <Text>{category.rewardSecond} &euro;</Text>
                      </Table.Td>
                      <Table.Td ta="center">
                        <Text>{category.rewardSemi} &euro;</Text>
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
