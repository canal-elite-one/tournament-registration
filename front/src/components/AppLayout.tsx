'use client';

import {AppShell, Group, Image, Anchor, Text, Container} from '@mantine/core';
import {SidebarLinks} from './SidebarLinks';

export default function AppLayout({children}: { children: React.ReactNode }) {
  return (
      <AppShell header={{height: 60}} padding={0} >
        {/* HEADER */}
        <AppShell.Header className="bg-white shadow sticky top-0 z-50">
          <Group justify="space-between" align="center" h="100%" px="md">
            {/* Left: Logo and Title */}
            <Anchor href="/" className="flex items-center no-underline"
                    style={{textDecoration: 'none', textDecorationLine: 'none'}}>
              <Image
                  src="/static/logo-48x48.png"
                  alt="USKB Logo"
                  height={40}
                  width={40}
                  className="mr-2"
              />
              <h1 className="text-lg font-semibold text-[#1836a9]">
                Tournoi USKB
              </h1>
            </Anchor>

            {/* Right: Navigation and Actions */}
            <Group>
              <SidebarLinks/>
            </Group>
          </Group>
        </AppShell.Header>

        {/* MAIN CONTENT */}
        <AppShell.Main className="p-0 m-0">{children}</AppShell.Main>

        {/* FOOTER */}
        <footer className="bg-white border-t">
          <Container size="lg"
                     className="py-6 flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
            <div className="flex flex-col md:flex-row gap-3 md:gap-6 mb-4 md:mb-0">
              <Anchor href="/mentions-legales" className="hover:underline">Mentions
                légales</Anchor>
              <Anchor href="/cgv" className="hover:underline">Conditions générales de
                vente</Anchor>
              <Anchor href="/confidentialite" className="hover:underline">Politique de
                confidentialité</Anchor>
            </div>
            <Text className="text-center md:text-right">
              🔒 Paiement sécurisé par
              Stripe &nbsp;|&nbsp; © {new Date().getFullYear()} USKB
            </Text>
          </Container>
        </footer>
      </AppShell>
  );
}
