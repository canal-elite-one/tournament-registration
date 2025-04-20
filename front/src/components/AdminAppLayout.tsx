"use client";

import {Anchor, AppShell, Box, Group, Image} from "@mantine/core";
import { AdminSidebarLinks } from "@/components/AdminSidebarLinks";
import { UserButton } from "@/components/UserButton";

export default function AdminAppLayout({
                                         children,
                                       }: {
  children: React.ReactNode;
}) {

  return (
      <AppShell
          layout="default"
          padding="md"
          header={{ height: 60 }}
          navbar={{
            width: 300,
            breakpoint: "xs",
          }}
      >
        {/* HEADER */}
        <AppShell.Header>
          <Group h="100%" px="md">
            <Anchor href="/admin" className="flex items-center no-underline"
                    style={{textDecoration: 'none'}}>
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
          </Group>
        </AppShell.Header>

        {/* SIDEBAR */}
        <AppShell.Navbar p="md">
          <Box
              h="100%"
              style={{ display: "flex", flexDirection: "column" }}
          >
            <AdminSidebarLinks />
            <Box mt="auto">
              <UserButton />
            </Box>
          </Box>
        </AppShell.Navbar>

        {/* MAIN CONTENT */}
        <AppShell.Main>{children}</AppShell.Main>
      </AppShell>
  );
}
