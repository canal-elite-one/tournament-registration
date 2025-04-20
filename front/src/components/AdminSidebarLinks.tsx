"use client";

import { JSX } from "react";
import {
  ScrollArea,
  Box,
  NavLink,
} from "@mantine/core";
import {
  IconHome, IconUser,
} from "@tabler/icons-react";
import { usePathname } from "next/navigation";


function getNavLinks(
): {
  label: string;
  icon: JSX.Element;
  link?: string;
}[] {
    return [
      {
        label: "Accueil",
        icon: <IconHome size={16} />,
        link: `/admin`,
      },
      {
        label: "Joueurs",
        icon: <IconUser size={16} />,
        link: `/admin/joueurs`,
      },
      {
        label: "Categories",
        icon: <IconUser size={16} />,
        link: `/admin/categories`,
      },
    ];
}

export function AdminSidebarLinks() {
  const pathname = usePathname(); // Get current URL path

  return (
      <ScrollArea>
        <Box className="px-3 py-2 space-y-1">
          {getNavLinks().map((item) =>
              (
                  // Top-Level Menu Items
                  <NavLink
                      key={item.label}
                      label={item.label}
                      component="a"
                      href={item.link}
                      active={pathname === item.link}
                      leftSection={item.icon}
                      className="px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100 transition"
                  />
              ),
          )}
        </Box>
      </ScrollArea>
  );
}
