"use client";

import {Badge, Table} from "@mantine/core";
import { CategoryMetrics } from "@/app/admin/page";


export default function CategoryMetricsTable({ categoryMetrics }: { categoryMetrics: CategoryMetrics[] }) {
  const getBadgeColor = (fillRate: number) => {
    if (fillRate >= 100) return "red";
    if (fillRate >= 80) return "yellow";
    return "green";
  };

  return (
      <div className="overflow-x-auto rounded-lg">
        <Table withColumnBorders withRowBorders highlightOnHover className="w-full">
          <Table.Thead>
            <Table.Tr>
              <Table.Th ta="center">ID</Table.Th>
              <Table.Th ta="center">Tableau</Table.Th>
              <Table.Th ta="center">Taux de remplissage</Table.Th>
              <Table.Th ta="center">Nombre d&apos;inscrits</Table.Th>
              <Table.Th ta="center">Liste d&apos;attente</Table.Th>
              <Table.Th ta="center">Inscriptions payées</Table.Th>
            </Table.Tr>
          </Table.Thead>

          <Table.Tbody>
            {categoryMetrics.map((item) => (
                <Table.Tr key={item.categoryId}>
                  <Table.Td className="text-sm text-gray-900">
                    {item.categoryId}
                  </Table.Td>
                  <Table.Td className="text-sm text-gray-900">
                    {item.alternateName || item.categoryId}
                  </Table.Td>
                  <Table.Td className="text-sm text-gray-900 text-center">
                    <Badge color={getBadgeColor(item.fillRate)} variant="light">
                      {item.fillRate}%
                    </Badge>
                  </Table.Td>
                  <Table.Td className="text-sm text-gray-900">
                    {item.numberOfEntries}
                  </Table.Td>
                  <Table.Td className="text-sm text-gray-900">
                    {item.numberInWaitingList}
                  </Table.Td>
                  <Table.Td className="text-sm text-gray-900">
                    {item.numberOfPaidEntries}
                  </Table.Td>
                </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </div>
  );
}