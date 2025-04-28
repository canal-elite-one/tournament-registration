"use client";

import { Box, Stack, NavLink, Button } from "@mantine/core";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";

const links = [
  { label: "Dashboard", href: "/admin" },
  { label: "Joueurs", href: "/admin/joueurs" },
  { label: "Categories", href: "/admin/categories" },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
      <Box
          w={250}
          p="xs"
          h="100%"
          style={{ display: "flex", flexDirection: "column" }}
      >
        <Stack gap="xs" style={{ flexGrow: 1 }}>
          {links.map((link) => (
              <NavLink
                  key={link.href}
                  label={link.label}
                  active={pathname === link.href}
                  href={link.href}
                  component="a"
              />
          ))}
        </Stack>

        <Box pt="sm" mt="auto">
          <Button
              fullWidth
              variant="light"
              color="red"
              onClick={() => signOut({ callbackUrl: "/admin/login" })}
          >
            Logout
          </Button>
        </Box>
      </Box>
  );
}
