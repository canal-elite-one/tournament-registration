"use client";

import {
  Table,
  Text,
  Button,
  TextInput,
  NumberInput,
  Checkbox,
  Modal,
  Group,
} from "@mantine/core";
import { DateTimePicker } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { useState } from "react";

export interface CategoryForm {
  id: string;
  alternateName: string;
  color: string;
  minPoints: number;
  maxPoints: number;
  startTime: Date;
  womenOnly: boolean;
  entryFee: number;
  lateFee: number;
  rewardFirst: number;
  rewardSecond: number;
  rewardSemi: number;
  rewardQuarter: number;
  maxPlayers: number;
  overbookingPercentage: number;
}

export default function AdminSetCategoriesPage() {
  const [categories, setCategories] = useState<CategoryForm[]>([]);
  const [confirmRemove, setConfirmRemove] = useState(false);

  const addFormRow = () => {
    setCategories([
      ...categories,
      {
        id: "",
        alternateName: "",
        color: "",
        minPoints: 0,
        maxPoints: 9999,
        startTime: new Date(),
        womenOnly: false,
        entryFee: 0,
        lateFee: 0,
        rewardFirst: 0,
        rewardSecond: 0,
        rewardSemi: 0,
        rewardQuarter: 0,
        maxPlayers: 0,
        overbookingPercentage: 0,
      },
    ]);
  };

  const removeFormRow = () => {
    setConfirmRemove(false);
    setCategories(categories.slice(0, -1));
    notifications.show({
      title: "Ligne supprimée",
      message: "La dernière catégorie a été supprimée.",
      color: "red",
    });
  };

  const handleChange = (index: number, field: keyof CategoryForm, value: any) => {
    setCategories((prev) => {
      const updated = [...prev];
      updated[index] = {
        ...updated[index],
        [field]: value,
      };
      return updated;
    });
  };

  const submitForm = async () => {
    if (categories.length === 0) {
      notifications.show({
        title: "Erreur",
        message: "Aucune catégorie à enregistrer.",
        color: "red",
      });
      return;
    }

    const response = await fetch("/api/admin/categories", {
      method: "POST",
      body: JSON.stringify({
        categories: categories
      }),
    });

    if (response.ok) {
      console.log("Successfully saved categories");
    } else {
      console.log("Error creating categories.");
    }
  };

  return (
      // <div className="flex justify-center bg-gray-50 px-4 sm:px-6 min-h-screen py-10 font-sans antialiased">
        <div className="bg-white rounded-lg shadow-md w-full p-4 sm:p-6 space-y-6">
          <Text size="xl" fw={700} className="text-center text-gray-800 mb-6">
            Tableaux
          </Text>

          <div className="overflow-x-auto rounded-lg">
            <Table.ScrollContainer minWidth={800}>
              <Table withColumnBorders withRowBorders highlightOnHover className="w-full">
                <Table.Thead>
                  <Table.Tr>
                    {[
                      "Identifiant",
                      "Nom alternatif",
                      "Couleur",
                      "Points min",
                      "Points max",
                      "Début",
                      "Féminin ?",
                      "Coût",
                      "Surcoût",
                      "Prix 1er",
                      "Prix 2e",
                      "Prix 1/2",
                      "Prix 1/4",
                      "Max inscrits",
                      "Surbooking (%)",
                    ].map((header) => (
                        <Table.Th key={header} className="text-center text-sm">{header}</Table.Th>
                    ))}
                  </Table.Tr>
                </Table.Thead>

                <Table.Tbody>
                  {categories.map((category, index) => (
                      <Table.Tr key={index}>
                        <Table.Td>
                          <TextInput
                              value={category.id}
                              onChange={(e) => handleChange(index, "id", e.currentTarget.value)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <TextInput
                              value={category.alternateName}
                              onChange={(e) => handleChange(index, "alternateName", e.currentTarget.value)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <TextInput
                              value={category.color}
                              onChange={(e) => handleChange(index, "color", e.currentTarget.value)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.minPoints}
                              onChange={(val) => handleChange(index, "minPoints", val)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.maxPoints}
                              onChange={(val) => handleChange(index, "maxPoints", val)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <DateTimePicker
                              value={category.startTime}
                              onChange={(date) => handleChange(index, "startTime", date)}
                              placeholder="Début"
                              size="sm"
                              radius="md"
                              dropdownType="popover"
                              className="w-full"
                          />
                        </Table.Td>
                        <Table.Td>
                          <Checkbox
                              checked={category.womenOnly}
                              onChange={(e) => handleChange(index, "womenOnly", e.currentTarget.checked)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.entryFee}
                              onChange={(val) => handleChange(index, "entryFee", val)}
                              step={0.5}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.lateFee}
                              onChange={(val) => handleChange(index, "lateFee", val)}
                              step={0.5}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.rewardFirst}
                              onChange={(val) => handleChange(index, "rewardFirst", val)}
                              step={0.01}
                              min={0}
                              allowDecimal
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.rewardSecond}
                              onChange={(val) => handleChange(index, "rewardSecond", val)}
                              step={0.01}
                              min={0}
                              allowDecimal
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.rewardSemi}
                              onChange={(val) => handleChange(index, "rewardSemi", val)}
                              step={0.01}
                              min={0}
                              allowDecimal
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.rewardQuarter}
                              onChange={(val) => handleChange(index, "rewardQuarter", val)}
                              step={0.01}
                              min={0}
                              allowDecimal
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.maxPlayers}
                              onChange={(val) => handleChange(index, "maxPlayers", val)}
                          />
                        </Table.Td>
                        <Table.Td>
                          <NumberInput
                              value={category.overbookingPercentage}
                              onChange={(val) => handleChange(index, "overbookingPercentage", val)}
                              step={0.01}
                              min={0}
                              allowDecimal
                          />
                        </Table.Td>
                      </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Table.ScrollContainer>
          </div>

          <Group justify="flex-end" gap="md">
            <Button color="red" variant="outline" onClick={() => setConfirmRemove(true)}>
              -
            </Button>
            <Button color="blue" variant="outline" onClick={addFormRow}>
              +
            </Button>
            <Button className="bg-blue-950 hover:bg-blue-700" onClick={submitForm}>
              Enregistrer les catégories
            </Button>
          </Group>
        {/*</div>*/}

        {/* Confirmation Modal */}
        <Modal
            opened={confirmRemove}
            onClose={() => setConfirmRemove(false)}
            title="Confirmer la suppression"
            centered
        >
          <Text>Voulez-vous vraiment supprimer la dernière catégorie ?</Text>
          <Group  mt="md" justify="space-between" gap="sm">
            <Button variant="default" onClick={() => setConfirmRemove(false)}>
              Annuler
            </Button>
            <Button color="red" onClick={removeFormRow}>
              Supprimer
            </Button>
          </Group>
        </Modal>
      </div>
  );
}
