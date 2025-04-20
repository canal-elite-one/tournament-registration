"use client";

import { Avatar, Button, Loader, Menu } from "@mantine/core";
import { IconLogout } from "@tabler/icons-react";
import { useState } from "react";
import {signOut, useSession} from "next-auth/react";

export function UserButton() {
  const [loading, setLoading] = useState(false);
  const { data: session } = useSession();

  const handleLogout = async () => {
    setLoading(true);
    await signOut({ callbackUrl: "/admin/login" }); // 👈 redirect after logout
  };

  return (
      <Menu shadow="md" width={200}>
        <Menu.Target>
          <Button variant="subtle" leftSection={<Avatar size="sm" />}>
            {session?.user?.email ?? "User"}
          </Button>
        </Menu.Target>

        <Menu.Dropdown>
          <Menu.Label>Config</Menu.Label>
          <Menu.Item
              color="red"
              leftSection={loading ? <Loader size="xs" /> : <IconLogout size={14} />}
              onClick={handleLogout}
              disabled={loading}
          >
            Logout
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>
  );
}
