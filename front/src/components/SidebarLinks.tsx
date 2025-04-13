"use client";

import {Group} from "@mantine/core";
import {IconHome, IconContract, IconMail} from "@tabler/icons-react";
import {usePathname} from "next/navigation";

function getNavLinks() {
  return [
    {
      label: "Accueil",
      icon: <IconHome size={16}/>,
      link: `/`,
    },
    {
      label: "Règlement",
      icon: <IconContract size={16}/>,
      link: `/reglement`,
    },
    {
      label: "Contact",
      icon: <IconMail size={16}/>,
      link: `/contact`,
    }
  ];
}

export function SidebarLinks({onClickLink}: { onClickLink?: () => void }) {
  const pathname = usePathname();

  return (
      <Group className="gap-4 flex-col md:flex-row justify-center items-center h-full">
      {getNavLinks().map((item) => {
          const isActive = pathname === item.link;

          return (
              <a
                  key={item.label}
                  href={item.link}
                  onClick={onClickLink}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md transition
              ${isActive ? "bg-gray-100 text-[#1836a9] font-medium" : "text-gray-700"}
              hover:bg-gray-100
            `}
              >
                {item.icon}
                <span>{item.label}</span>
              </a>
          );
        })}
      </Group>
  );
}
