import Image from "next/image";
import {Card, Text, Group, Button} from "@mantine/core";
import Link from "next/link";

export default function ErrorPage() {
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
          Une erreur est survenue
        </Text>
      </Group>

      <Text mb="md" size="sm">
        Nous sommes désolés, une erreur est survenue lors du traitement de votre demande.
      </Text>

      <Text mb="md" size="sm">
        Merci de contacter les organisateurs afin de résoudre le problème.
      </Text>

      <Group justify="center" mt="lg">
        <Button
            component={Link}
            href="/contact"
            variant="light"
            color="blue"
            radius="md"
        >
          Contacter les organisateurs
        </Button>
      </Group>
    </Card>
  );
}
