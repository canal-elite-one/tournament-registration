"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Button,
  Modal,
  Select,
  Text,
  Group,
  Stack,
  SegmentedControl,
  Table,
  Badge,
  Tooltip
} from "@mantine/core";
import { DateTimePicker } from "@mantine/dates";
import { useDisclosure } from '@mantine/hooks';

import { AdminPlayer } from "@/backend_api/backend"; // Adjust import path as needed
import { showNotification } from "@mantine/notifications";
import {IconCheck, IconX} from "@tabler/icons-react";
import {Spotlight, SpotlightActionData} from "@mantine/spotlight";

export default function AdminPlayersTable({ players }: { players: AdminPlayer[] }) {
  // for modal
  const [opened, { open, close }] = useDisclosure(false);
  const [selectedPlayer, setSelectedPlayer] = useState<AdminPlayer | null>(null);
  const [template, setTemplate] = useState<string | null>(null);
  const [warningDeadline, setWarningDeadline] = useState<Date | null>(null);
  const [cancelModalOpened, { open: openCancelModal, close: closeCancelModal }] = useDisclosure(false);
  const [playerToUnregister, setPlayerToUnregister] = useState<AdminPlayer | null>(null);

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
        if (filter === "paid") return player.remainingAmount <= 0;
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

  const spotlightActions: SpotlightActionData[] = players.map((player) => ({
    id: `${player.licenceNo}`,
    label: `${player.firstName} ${player.lastName} (${player.licenceNo})`,
    description: `${player.club}`,
    onClick: () => router.push(`/admin/joueurs/${player.licenceNo}`),
  }));

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
                <Table.Th ta="center">
                  <Text c="white" fw={600}>#</Text>
                </Table.Th>
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
                <Table.Th ta="center"><Text c="white" fw={600}>Actions</Text></Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {filteredPlayers.map((player, index) => (
                  <Table.Tr
                      key={player.licenceNo}
                      onClick={() => router.push(`/admin/joueurs/${player.licenceNo}`)}
                      className="cursor-pointer hover:bg-gray-100 transition-colors"
                  >
                    <Table.Td ta="center">{index + 1}</Table.Td>
                    <Table.Td>{player.lastName}</Table.Td>
                    <Table.Td>{player.firstName}</Table.Td>
                    <Table.Td>{player.licenceNo}</Table.Td>
                    <Table.Td>{player.club}</Table.Td>
                    <Table.Td className="text-center">
                      {player.remainingAmount <= 0 ? (
                          <Badge color="green" variant="light">Payé</Badge>
                      ) : (
                          <Badge color="red" variant="light">Non payé</Badge>
                      )}
                    </Table.Td>
                    <Table.Td>{player.remainingAmount.toFixed(2)}</Table.Td>
                    <Table.Td ta="center">
                      <Tooltip
                          label="Le joueur a déjà payé"
                          disabled={player.remainingAmount !== 0}
                          withArrow
                          position="top"
                      >
                        <Button
                            onClick={(e) => {
                              e.stopPropagation();
                              if (player.remainingAmount <= 0) return;
                              setSelectedPlayer(player);
                              setTemplate(null);
                              setWarningDeadline(null);
                              open();
                            }}
                            disabled={player.remainingAmount <= 0}
                            color={player.remainingAmount <= 0 ? "gray" : "blue"}
                            variant="filled"
                            size="xs"
                        >
                          Rappel
                        </Button>
                      </Tooltip>
                      <Tooltip
                          label="Le joueur a déjà payé"
                          disabled={player.remainingAmount !== 0}
                          withArrow
                          position="top"
                      >
                        <Button
                            onClick={(e) => {
                              e.stopPropagation();
                              setPlayerToUnregister(player);
                              openCancelModal();
                            }}
                            disabled={player.remainingAmount <= 0}
                            color="red"
                            variant="filled"
                            size="xs"
                            ml="xs"
                        >
                          Désinscrire
                        </Button>
                      </Tooltip>
                    </Table.Td>
                  </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>

        <Modal
            opened={opened}
            onClose={close}
            title={`Envoyer un message à ${selectedPlayer?.firstName} ${selectedPlayer?.lastName}`}
            centered
        >
          <Stack>
            <Select
                label="Modèle"
                placeholder="Choisissez un modèle"
                data={[
                  { label: "Lien de paiement", value: "payment-link" },
                  { label: "Dernier rappel", value: "last-warning" },
                ]}
                value={template}
                onChange={setTemplate}
            />

            {template === "last-warning" && (
                <DateTimePicker
                    label="Date limite de paiement"
                    value={warningDeadline}
                    onChange={setWarningDeadline}
                    placeholder="Sélectionnez une date et une heure"
                    required
                />
            )}

            <Group justify="right" mt="md">
              <Button
                  onClick={async () => {
                    if (!selectedPlayer || !template) return;

                    if (template === "last-warning") {
                      if (!warningDeadline) {
                        alert("Veuillez sélectionner une date limite");
                        return;
                      }
                    }

                    const response = await fetch("/api/admin/player/send-payment-link", {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({
                        licenceNo: selectedPlayer.licenceNo,
                        template: template,
                        deadline: warningDeadline ? warningDeadline.toISOString() : null,
                      }),
                    });

                    if (response.ok) {
                      showNotification({
                        title: 'Message envoyé',
                        message: `Un email a été envoyé à ${selectedPlayer.email}`,
                        color: 'green',
                        icon: <IconCheck size={18} />,
                        autoClose: 30000,
                      });
                    } else {
                      showNotification({
                        title: 'Erreur',
                        message: "Une erreur est survenue lors de l'envoi de l'email",
                        color: 'red',
                        icon: <IconX size={18} />,
                        autoClose: 30000,
                      });
                    }

                    close();
                  }}
                  disabled={template === "last-warning" && !warningDeadline}
              >
                Envoyer
              </Button>
            </Group>
          </Stack>
        </Modal>
        <Modal
            opened={cancelModalOpened}
            onClose={closeCancelModal}
            title={`Annuler l'inscription de ${playerToUnregister?.firstName} ${playerToUnregister?.lastName} ?`}
            centered
        >
          <Text>Êtes-vous sûr(e) de vouloir annuler cette inscription ? Cette action est irréversible.</Text>
          <Group justify="right" mt="md">
            <Button onClick={closeCancelModal} variant="default">Annuler</Button>
            <Button
                color="red"
                onClick={async () => {
                  if (!playerToUnregister) return;

                  const response = await fetch(`/api/admin/player/unregister`, {
                    method: "POST",
                    body: JSON.stringify({
                      licenceNo: playerToUnregister.licenceNo,
                    }),
                  });

                  if (response.ok) {
                    showNotification({
                      title: 'Inscription annulée',
                      message: `Le joueur ${playerToUnregister.firstName} ${playerToUnregister.lastName} a été désinscrit.`,
                      color: 'green',
                      icon: <IconCheck size={18} />,
                      autoClose: 30000,
                    });
                    router.refresh();
                  } else {
                    showNotification({
                      title: 'Erreur',
                      message: "Une erreur est survenue lors de la désinscription",
                      color: 'red',
                      icon: <IconX size={18} />,
                      autoClose: 30000,
                    });
                  }

                  closeCancelModal();
                }}
            >
              Confirmer
            </Button>
          </Group>
        </Modal>

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
