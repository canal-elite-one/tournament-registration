"use client";

import { Card, Text, List, Anchor, Group } from "@mantine/core";

export default function EntriesSummary({
                                         entries,
                                         emailContact,
                                         licenceNo,
                                       }: {
  entries: { id: string; label: string }[];
  emailContact?: string;
  licenceNo: string;
}) {
  return (
    <Card
        className="max-w-xl mx-auto mt-8 sm:mt-12"
        shadow="md"
        padding="lg"
        radius="lg"
        withBorder
    >
      <Group mb="xl" className="text-center space-y-2">
        <Text size="xl" fw={700} className="text-gray-800">
          Bonjour {licenceNo} !
        </Text>
        <Text size="lg" fw={600} className="text-gray-700">
          Vous êtes inscrit(s) aux tableaux suivants :
        </Text>
      </Group>

      <List
          spacing="sm"
          listStyleType="disc"
          className="pl-6 mb-6 text-gray-700 text-sm sm:text-base leading-relaxed"
      >
        {entries.map((entry) => (
            <List.Item key={entry.id}>{entry.label}</List.Item>
        ))}
      </List>

      <Text c="gray.6" size="sm" className="leading-relaxed">
        Si vous souhaitez modifier vos informations ou vos inscriptions, veuillez{" "}
        <Anchor
            href={`mailto:${emailContact}`}
            c="blue.5"
            underline="hover"
            fw={700}
        >
          envoyer un mail
        </Anchor>{" "}
        aux organisateurs à l&apos;adresse suivante :{" "}
        <Anchor
            href={`mailto:${emailContact}`}
            c="blue.5"
            underline="hover"
            fw={700}
        >
          {emailContact}
        </Anchor>.
      </Text>
    </Card>
  );
}
