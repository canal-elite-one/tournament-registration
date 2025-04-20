"use client";

import Image from "next/image";
import { Card, Text, List, Anchor, Group, ActionIcon } from "@mantine/core";

export default function ContactCard({
                                      contactEmail,
                                      contactWebsite,
                                      contactInsta,
                                      contactLinkedIn,
                                    }: {
  contactEmail?: string;
  contactWebsite?: string;
  contactInsta?: string;
  contactLinkedIn?: string;
}) {
  return (
      <Card
          className="max-w-md mx-auto mt-8 sm:mt-12"
          shadow="md"
          padding="lg"
          radius="lg"
          withBorder
      >
        <Group align="center" mb="md" className="mb-6">
          <Image
              src="/static/logo.png"
              alt="Logo"
              width={48}
              height={48}
              className="mr-4"
              priority
          />
          <Text size="lg" fw={700}>
            Contactez l&apos;USKB
          </Text>
        </Group>

        <Text mb="md" size="sm">
          Vous pouvez contacter les organisateurs du tournoi de la façon suivante :
        </Text>

        <List spacing="xs" listStyleType="disc" className="pl-6 mb-6 text-sm sm:text-base">
          <List.Item>
            Par mail :{" "}
            <Anchor
                href={`mailto:${contactEmail}`}
                c="blue.5"
                underline="hover"
                size="sm"
            >
              {contactEmail}
            </Anchor>
          </List.Item>
          <List.Item>
            <Anchor
                href={contactWebsite}
                target="_blank"
                rel="noopener noreferrer"
                c="blue.5"
                underline="hover"
                size="sm"
            >
              Site web de l&apos;USKB
            </Anchor>
          </List.Item>
          <List.Item>
            Retrouvez-nous sur les réseaux sociaux :
            <Group mt="xs">
              <ActionIcon
                  variant="transparent"
                  component="a"
                  href={contactInsta}
                  target="_blank"
                  rel="noopener noreferrer"
                  size="lg"
                  radius="xl"
                  aria-label="Instagram"
              >
                <Image
                    src="/static/instagram-logo.png"
                    alt="Instagram Logo"
                    width={24}
                    height={24}
                />
              </ActionIcon>
              <ActionIcon
                  variant="transparent"
                  component="a"
                  href={contactLinkedIn}
                  target="_blank"
                  rel="noopener noreferrer"
                  size="lg"
                  radius="xl"
                  aria-label="LinkedIn"
              >
                <Image
                    src="/static/linkedin-logo.png"
                    alt="LinkedIn Logo"
                    width={24}
                    height={24}
                />
              </ActionIcon>
            </Group>
          </List.Item>
        </List>
      </Card>
  );
}
